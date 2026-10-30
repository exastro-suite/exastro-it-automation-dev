#   Copyright 2026 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
OASE向けドキュメント(documents/{ja,en}/menu-reference, tool-reference)のテスト

Agentic AIはこれらのドキュメントを get-document / search-docs で読み、書かれた
手順・JSONの例をそのまま使ってOASEの設定を登録する。そのため、

- 日英の両方がそろい、get-document で取得できること
- 本文中で get-document の取得先として案内しているパスが、実際に解決できること
- JSONの例がJSONとして読めること(壊れた例はそのまま登録エラーになる)
- ルール判定を止める書き方(結論ラベルの空リスト "[]")を例に含めないこと
- 日英で節の構成がずれていないこと

を確認する。get-document の取得は tools/search_documents.py の実装をそのまま使い、
DOCUMENT_PATH だけをリポジトリ内の documents/<言語> に差し替える。

Tests for the OASE documents (documents/{ja,en}/menu-reference, tool-reference).
Agentic AI reads these documents with get-document / search-docs and uses the
procedures and JSON examples as they are, so this checks that both languages exist
and can be retrieved, that the paths referenced for get-document resolve, that JSON
examples parse, that no example uses an empty conclusion label list "[]" (which
stops rule evaluation), and that the Japanese and English section structures match.
"""
import json
import re
from pathlib import Path

import pytest

from tools import search_documents

DOCUMENTS_ROOT = Path(__file__).resolve().parent.parent / "documents"
LANGUAGES = ("ja", "en")

# OASEのシナリオ対応で追加・追記したドキュメント
OASE_DOCUMENTS = (
    "menu-reference/event_collection.md",
    "menu-reference/label_creation.md",
    "menu-reference/labeling.md",
    "menu-reference/deduplication.md",
    "menu-reference/filter.md",
    "menu-reference/action.md",
    "menu-reference/rule.md",
    "menu-reference/oase_scenario_building.md",
    "tool-reference/maintenance-all.md",
    "tool-reference/menu-filter.md",
)

# 本文中で「get-documentで〜を取得する」と案内しているパス(バッククォートで囲まれたもの)
REFERENCE_PATTERN = re.compile(r"`((?:[A-Za-z0-9_\-]+/)+[A-Za-z0-9_\-]+\.md)`")
JSON_BLOCK_PATTERN = re.compile(r"```json\n(.*?)```", re.S)
EMPTY_CONCLUSION_LABEL_PATTERN = re.compile(r'"conclusion_label_settings"\s*:\s*"\[\s*\]"')
SECTION_PATTERN = re.compile(r"^(#{1,6}) ", re.M)


def _read(lang, source):
    return (DOCUMENTS_ROOT / lang / source).read_text(encoding="utf-8")


def _json_blocks(text):
    return JSON_BLOCK_PATTERN.findall(text)


def _parse_json_example(block):
    """JSONの例を読み、値のリストを返す。読めなければ json.JSONDecodeError を送出する。

    ドキュメントには次の3つの書き方がある。
    - 1つのJSON値
    - キーと値の一部だけ(例: "ttl": "3600")。オブジェクトの中身として読む
    - 1行に1つのJSON値を並べ、// のコメント行で説明したもの
    """
    lines = [line for line in block.splitlines() if not line.strip().startswith("//")]
    body = "\n".join(lines).strip()
    if not body:
        return []
    try:
        return [json.loads(body)]
    except json.JSONDecodeError as e:
        first_error = e
    try:
        return [json.loads("{" + body + "}")]
    except json.JSONDecodeError:
        pass
    try:
        return [json.loads(line) for line in lines if line.strip()]
    except json.JSONDecodeError:
        raise first_error


def _cases():
    return [(lang, source) for lang in LANGUAGES for source in OASE_DOCUMENTS]


def _case_id(case):
    return "{}:{}".format(*case)


@pytest.fixture
def document_path(monkeypatch):
    """get-document の検索対象をリポジトリ内の documents/<言語> に差し替える"""
    def _set(lang):
        monkeypatch.setattr(search_documents, "DOCUMENT_PATH", str(DOCUMENTS_ROOT / lang))
    return _set


class TestOaseDocumentsExist:
    @pytest.mark.parametrize("case", _cases(), ids=_case_id)
    def test_document_exists_and_has_title(self, case):
        # 正常系: 日英それぞれにファイルがあり、先頭行が見出し(# ...)であること
        lang, source = case
        path = DOCUMENTS_ROOT / lang / source
        assert path.is_file(), "missing: {}".format(path)
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith("# ")

    def test_same_file_set_in_both_languages(self):
        # 正常系: menu-reference / tool-reference のファイル構成が日英で一致すること
        for directory in ("menu-reference", "tool-reference"):
            ja = {p.name for p in (DOCUMENTS_ROOT / "ja" / directory).glob("*.md")}
            en = {p.name for p in (DOCUMENTS_ROOT / "en" / directory).glob("*.md")}
            assert ja == en, "{}: only ja={} only en={}".format(directory, sorted(ja - en), sorted(en - ja))


class TestGetDocument:
    @pytest.mark.parametrize("case", _cases(), ids=_case_id)
    def test_get_document_returns_full_text(self, mock_flask_g, document_path, case):
        # 正常系: get-document で取得でき、全文・ファイル名・ディレクトリが正しく返ること
        lang, source = case
        document_path(lang)

        result = search_documents.tool_get_document({"source": source}, {"user_id": "u1"})

        assert result["text"] == _read(lang, source)
        assert result["filename"] == Path(source).name
        assert result["directory"] == str(Path(source).parent)
        assert result["title"]
        assert result["message"] == "Document retrieved successfully."


class TestReferencedDocuments:
    @pytest.mark.parametrize("case", _cases(), ids=_case_id)
    def test_referenced_paths_resolve_with_get_document(self, mock_flask_g, document_path, case):
        # 正常系: 本文で取得先として案内しているパスが、get-document で実際に解決できること
        # (存在しないパスを案内すると、Agentic AIは Document not found で手順を読めない)
        lang, source = case
        document_path(lang)
        references = sorted(set(REFERENCE_PATTERN.findall(_read(lang, source))))

        unresolved = []
        for reference in references:
            try:
                search_documents._resolve_document_source(reference)
            except (ValueError, FileNotFoundError):
                unresolved.append(reference)

        assert unresolved == [], "{} references missing documents: {}".format(source, unresolved)

    def test_reference_pattern_detects_unresolvable_path(self, mock_flask_g, document_path):
        # 異常系: 存在しないパスは get-document で FileNotFoundError になり、
        # 上のテストで検出できること(テスト自体が空振りしていないことの確認)
        document_path("ja")
        assert REFERENCE_PATTERN.findall("`documents-menu/rule.md` と `menu-reference/rule.md`") == [
            "documents-menu/rule.md", "menu-reference/rule.md"
        ]
        with pytest.raises(FileNotFoundError):
            search_documents._resolve_document_source("documents-menu/rule.md")
        assert search_documents._resolve_document_source("menu-reference/rule.md").is_file()


class TestJsonExamples:
    @pytest.mark.parametrize("case", _cases(), ids=_case_id)
    def test_json_examples_are_valid_json(self, case):
        # 正常系: ```json のコードブロックがすべてJSONとして読めること
        lang, source = case
        broken = []
        for index, block in enumerate(_json_blocks(_read(lang, source))):
            try:
                _parse_json_example(block)
            except json.JSONDecodeError as e:
                broken.append("block {}: {}".format(index, e))
        assert broken == [], "{} has invalid JSON examples: {}".format(source, broken)


class TestParseJsonExample:
    def test_whole_value(self):
        # 正常系: 1つのJSON値として読めること
        assert _parse_json_example('{"a": 1}') == [{"a": 1}]

    def test_key_value_fragment(self):
        # 正常系: キーと値の一部だけの例は、オブジェクトの中身として読めること
        assert _parse_json_example('"ttl": "3600",\n"parameter": "{}"\n') == [{"ttl": "3600", "parameter": "{}"}]

    def test_one_value_per_line_with_comments(self):
        # 正常系: // のコメント行を除き、1行に1つずつのJSON値として読めること
        block = '// 完全一致\n{"a": {"NORMAL": "x"}}\n\n// 全件\n{}\n'
        assert _parse_json_example(block) == [{"a": {"NORMAL": "x"}}, {}]

    def test_empty_block(self):
        # 境界値: コメントだけ・空のブロックは値0件として扱うこと
        assert _parse_json_example("// comment only\n") == []

    def test_broken_json_raises(self):
        # 異常系: どの書き方でも読めない例は JSONDecodeError になること
        with pytest.raises(json.JSONDecodeError):
            _parse_json_example('{"a": 1,}')


class TestConclusionLabelSettings:
    @pytest.mark.parametrize("case", _cases(), ids=_case_id)
    def test_no_empty_conclusion_label_examples(self, case):
        # 異常系の防止: conclusion_label_settings に "[]" を渡す例が無いこと
        # ("[]" はDBにNULLで保存され、判定処理が TypeError でワークスペース全体の判定を止める)
        lang, source = case
        text = _read(lang, source)
        for block in _json_blocks(text):
            assert not EMPTY_CONCLUSION_LABEL_PATTERN.search(block), "{}: {}".format(source, block)

    def test_rule_reference_explains_empty_list_is_forbidden(self):
        # 正常系: rule.md の conclusion_label_settings 節に、空リストの禁止と代わりの値が書かれていること
        safe_value = '"[[\\"_exastro_host\\", \\"{{ A._exastro_host }}\\"]]"'
        for lang in LANGUAGES:
            text = _read(lang, "menu-reference/rule.md")
            section = text.split("## conclusion_label_settings column", 1)[1].split("\n## ", 1)[0]
            assert '`"[]"`' in section
            assert "NULL" in section
            assert safe_value in section

    def test_pattern_detects_empty_list(self):
        # 異常系: 検出用のパターンが空リストの書き方の揺れ(空白の有無)を検出できること
        assert EMPTY_CONCLUSION_LABEL_PATTERN.search('"conclusion_label_settings": "[]"')
        assert EMPTY_CONCLUSION_LABEL_PATTERN.search('"conclusion_label_settings":"[ ]"')
        assert not EMPTY_CONCLUSION_LABEL_PATTERN.search(
            '"conclusion_label_settings": "[[\\"_exastro_host\\", \\"{{ A._exastro_host }}\\"]]"'
        )


class TestLanguageConsistency:
    @pytest.mark.parametrize("source", OASE_DOCUMENTS)
    def test_section_structure_matches(self, source):
        # 正常系: 日英で見出しのレベルの並びが一致すること(片方だけ節を追加・削除していない)
        ja = SECTION_PATTERN.findall(_read("ja", source))
        en = SECTION_PATTERN.findall(_read("en", source))
        assert ja == en

    @pytest.mark.parametrize("source", OASE_DOCUMENTS)
    def test_json_examples_match(self, source):
        # 正常系: 日英でJSONの例の数とキーの構成が一致すること
        # (値は表示名の翻訳で異なることがあるため、キーだけを比べる)
        def keys(value):
            if isinstance(value, dict):
                return {k: keys(v) for k, v in value.items()}
            if isinstance(value, list):
                return [keys(v) for v in value]
            return None

        ja = [keys(v) for b in _json_blocks(_read("ja", source)) for v in _parse_json_example(b)]
        en = [keys(v) for b in _json_blocks(_read("en", source)) for v in _parse_json_example(b)]
        assert ja == en
