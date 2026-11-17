////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / ai_assistant_tool_display_html.js
//
//   -----------------------------------------------------------------------------------------------
//
//   Copyright 2026 NEC Corporation
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.
//
////////////////////////////////////////////////////////////////////////////////////////////////////

// 画面専用ツール「display_html」（チャット欄への任意HTML表示）。
//
// ・MCPサーバーではなく画面側（このクラス）で実行するツール。ツール定義（LLMへ渡す内容）と
//   その動作を1ファイルにまとめている。
// ・LLMへ渡す使い方・デザインのルールは description に持たせる（システムプロンプトは
//   プラットフォーム側が保持しており、画面側からは追記できないため）。
// ・LLMが生成したHTMLは信頼できない（プロンプトインジェクションで悪意あるHTMLになり得る）ため、
//   スクリプト実行を禁止した sandbox iframe ＋ CSP で隔離して表示する。
//   <script>・イベント属性は実行されず、外部リソースの読み込みも遮断される。スタイルも本体と干渉しない。
// ・表示専用のツールであり、表示内容やユーザーの操作結果はLLMには返らない（成功可否のみ返す）。
class AiAssistantToolDisplayHtml {
/*
##################################################
   ツール定義
##################################################
*/
static get toolName() {
    return 'display_html';
}
// 表示するHTMLのデザイン指針（LLMに毎回同じ体裁で作らせるための共通トークン）
static get designTokens() {
    return ':where(.exa-report){'
        + ' --accent:#335581; --accent-2:#4D6B91; --accent-soft:#8095B1;'
        + ' --text:#333; --muted:#6b7280;'
        + ' --border:#e2e8f0; --surface:#fff; --bg:#f7f9fa;'
        + ' --ok:#56B20C; --warn:#FFDD00; --danger:#CC1100;'
        + ' --radius:8px;'
        + ' }';
}
// LLMへ渡すツール定義（MCPのtools/listと同じ形式。inputSchemaはLLM層でinput_schemaへ変換される）
static get definition() {
    return {
        name: AiAssistantToolDisplayHtml.toolName,
        description: 'ユーザーの画面（チャット欄）に任意のHTMLを表示するための画面専用ツール。'
            + 'カード型レイアウト・複雑な入れ子構造・図解など、通常のMarkdownでは表現できないリッチな表現が必要なときだけ使う。'
            + '重要: 単純な表・箇条書き・見出し・通常の文章など、Markdownで表現できる内容にはこのツールを使わず、通常のテキスト応答（Markdown）で書くこと。特に表だけを見せたい場合はMarkdownの表を使い、このツールは使わないこと。'
            + '重要: このツールで表示した内容と同じもの（同じ表など）を、テキスト応答（Markdown）で重複して出力してはいけない。二重表示になる。'
            + 'このツールを使ったときは、テキスト側は短い導入・補足のみに留めること。'
            + '表示したHTMLは sandbox iframe で隔離されるため、アプリ本体のスタイルと相互に干渉しない。'
            + '注意: これは「表示」専用であり、表示したHTMLの内容やユーザーの操作結果はLLMには返らない（成功可否のみ返る）。'
            + 'ユーザーへの選択・同意確認には使わず、その場合は ask_user_choice を使うこと。'
            + '<script> やイベント属性（onclick等）は実行されず、外部リソース（外部URLの画像・CSS・フォント）も読み込まれないため、スタイルはインラインの <style> / style属性で完結させた静的なHTMLを渡すこと。画像が必要な場合はインラインSVGを使うこと。'
            + '\n【分量のルール】'
            + '\n・1回の応答で出力できる量には上限があり、長いHTMLを1回で渡すと引数が途中で切れて表示に失敗する。'
            + '\n・レポートなど内容が多いものは1回で渡さず、セクション単位（例：概要・指標／明細／分析・補足）に分けてこのツールを複数回呼び出すこと。1回に渡すHTMLは3000文字程度までを目安とする。'
            + '\n・分割した各回のHTMLは、それぞれ単体で完結した内容にすること（ルートの <div class="exa-report"> とデザイントークンの <style> は毎回含める）。'
            + '\n【デザイン統一のルール】'
            + '\n・毎回バラバラな見た目にせず、次の共通デザイン指針に従って統一感のある見た目にすること。'
            + '\n・必須: 全体を1つのルート <div class="exa-report"> で囲み、その先頭の <style> に次のデザイントークン（CSS変数）の定義をそのまま貼り付けてから内容を書き始めること。'
            + `\n${AiAssistantToolDisplayHtml.designTokens}`
            + '\n・var(--xxx) を使うときは、その変数の定義が上記 <style> 内にあることを出力直前に自己点検すること（未定義の変数を使うと色が出ず表示が崩れる）。'
            + '\n・トークンの意味：--accent＝アプリのメインカラーである紺、--accent-2＝差し色ブルー、--accent-soft＝薄い面、--text＝文字色、--muted＝補助文字、--border＝枠線、--surface＝カード面、--bg＝背景、--ok/--warn/--danger＝成功/注意/危険、--radius＝角丸。基本余白は16px。'
            + '\n・カードは「白背景・1px solid var(--border)・角丸 var(--radius)・内側余白16px・淡い影（例: box-shadow:0 1px 3px rgba(0,0,0,.06)）」で表現すること。'
            + '\n・セクション見出しやヘッダー帯にはメインカラーの紺（--accent）を用い、リンクやグラフのバーなどの差し色には --accent-2 を用いること。'
            + '\n・件数・成功/失敗などの指標は「大きな数字＋小さなラベル」のスタットカードで示すこと。'
            + '\n・グラフは外部ライブラリに依存できないため、インラインSVGまたはCSS（バーは background:var(--accent-2) と width:%）で描くこと。'
            + '\n・配色は上記トークンに限定し、多色の乱用や派手なグラデーションは避け、余白を十分にとって可読性を最優先とすること。',
        inputSchema: {
            type: 'object',
            properties: {
                title: {
                    type: 'string',
                    description: '表示内容の見出し（任意）。吹き出し上部に表示される。'
                },
                html: {
                    type: 'string',
                    description: '表示するHTML断片。<script>・イベント属性は実行されず、外部リソースは読み込まれない。'
                }
            },
            required: [ 'html' ]
        }
    };
}
/*
##################################################
   Constructor
##################################################
*/
// chat … AiAssistantChat（吹き出しの生成・スクロールはチャット側に委ねる）
constructor( chat ) {
    this.chat = chat;
}
/*
##################################################
   実行（HTMLの表示）
##################################################
*/
// LLMから渡されたHTMLを sandbox iframe 内に描画してチャット欄に表示し、
// LLMには「表示した」旨の tool_result を返す（表示内容自体はLLMに返さない）。
execute( toolUse ) {
    const input = toolUse.arguments ?? toolUse.input ?? {};
    const html = typeof input.html === 'string' ? input.html : '';
    const title = typeof input.title === 'string' ? input.title : '';

    // 待機中（思考中）インジケータが残っていれば消してから表示する。
    this.chat.elements.chatList
        ?.querySelectorAll('.aiAssistantChatItemLoading')
        .forEach(( item ) => item.remove() );

    const el = this.appendElement( html, title );
    if ( el ) setTimeout(() => { this.chat.scrollChatArea( el ); }, 100 );

    return {
        type: 'tool_result',
        tool_use_id: toolUse.id ?? '',
        content: getMessage.FTE14105
    };
}
/*
##################################################
   履歴からの復元
##################################################
*/
// 履歴復元時に表示バブルを再描画する（tool_result は返さない）。
resume( toolUse ) {
    const input = toolUse.arguments ?? toolUse.input ?? {};
    const html = typeof input.html === 'string' ? input.html : '';
    const title = typeof input.title === 'string' ? input.title : '';
    if ( !html && !title ) return;

    this.appendElement( html, title );
}
/*
##################################################
   表示バブル
##################################################
*/
// 表示バブルを生成してチャット欄へ追加する（ライブ表示・履歴復元で共用）。
appendElement( html, title ) {
    const chatList = this.chat.elements.chatList;
    if ( !chatList ) return null;

    const el = this.createElement( html, title );
    // 直前がアシスタントなら連続クラスを付与（他の吹き出しと同じ体裁）
    const prevItem = chatList.lastElementChild;
    if ( prevItem?.classList.contains('aiAssistantChatAssistantMessage') ) {
        el.classList.add('aiAssistantChatAssistantMessageChain');
    }
    chatList.append( el );
    return el;
}
// 表示バブル（アシスタントメッセージ枠 + sandbox iframe）を生成する。
createElement( html, title ) {
    const el = this.chat.createAssistantMessageElement('', false );
    const inner = el.querySelector('.aiAssistantChatAssistantMessageInner');
    inner.classList.add('aiAssistantChatDisplayHtmlInner');

    // ヘッダー（見出し ＋ PDFダウンロードボタン）。見出しが無くてもボタンは表示する。
    const header = document.createElement('div');
    header.classList.add('aiAssistantChatDisplayHtmlHeader');
    const titleEl = document.createElement('div');
    titleEl.classList.add('aiAssistantChatDisplayHtmlTitle');
    titleEl.innerText = title || '';
    header.appendChild( titleEl );
    header.insertAdjacentHTML('beforeend', fn.html.button(
        fn.html.icon('download'),
        'itaButton aiAssistantChatDisplayHtmlPdfButton',
        { type: 'displayHtmlPdf', action: 'default', title: getMessage.FTE14106 }
    ));
    inner.appendChild( header );

    const host = document.createElement('div');
    host.classList.add('aiAssistantChatDisplayHtmlHost');
    host.appendChild( this.createSandboxFrame( html, title ) );
    inner.appendChild( host );
    return el;
}
// sandbox iframe 内で表示するドキュメントのCSS。
contentCss() {
    return `
        html { overflow-y: hidden; }
        body {
            display: flow-root;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', Meiryo, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            word-break: break-word;
        }
        * { box-sizing: border-box; }
        img, svg, canvas, video { max-width: 100%; height: auto; }
        table { border-collapse: collapse; max-width: 100%; }
        th, td { padding: 4px 8px; border: 1px solid #ccc; }
        a { color: #005FD8; }
        pre { white-space: pre-wrap; word-break: break-word; }
        h1.aiAssistantPdfTitle { display: none; }
        @page { margin: 12mm; }
        @media print {
            html { overflow: visible; }
            h1.aiAssistantPdfTitle { display: block; font-size: 18px; margin: 0 0 12px; padding-bottom: 6px; border-bottom: 1px solid #ccc; }
        }
    `;
}
// iframe の srcdoc に設定する単独ドキュメントを組み立てる。
// ・CSP で外部リソースの読み込み（画像ビーコン等によるデータ送信）を遮断する。
//   LLM側のHTMLが別の CSP meta を含めても、CSP は厳しい方向にしか合成されないため緩められない。
// ・<base target="_blank"> でリンクは別タブで開く（チャット内の iframe 自体を遷移させない）。
// ・見出し（h1）は印刷（PDF出力）時のみ表示する。<title> はPDFの既定ファイル名に使われる。
buildDocument( html, title ) {
    const docTitle = ( title && title.trim() ) ? title.trim() : getMessage.FTE14107;
    return '<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
        + '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; font-src data:; form-action \'none\'; base-uri \'none\'">'
        + '<meta name="referrer" content="no-referrer">'
        + '<base target="_blank">'
        + `<title>${fn.escape( docTitle )}</title>`
        + `<style>${this.contentCss()}</style>`
        + '</head><body>'
        + ( title ? `<h1 class="aiAssistantPdfTitle">${fn.escape( title )}</h1>` : '')
        + html
        + '</body></html>';
}
// LLMが生成したHTMLを隔離して表示する sandbox iframe を生成する。
// ・allow-scripts を付けないため、<script>・イベント属性（onerror 等）・javascript: URL は一切実行されない。
// ・allow-same-origin は親から高さ計測・印刷を行うために付ける（スクリプトが動かないため親へは干渉できない）。
//   ※ allow-scripts と allow-same-origin を同時に付けると sandbox を抜けられるため、絶対に併用しないこと。
// ・allow-modals は print()（PDF出力）に必要。
// ・allow-popups / allow-popups-to-escape-sandbox はリンクを別タブで通常のページとして開くために付ける。
createSandboxFrame( html, title ) {
    const iframe = document.createElement('iframe');
    iframe.classList.add('aiAssistantChatDisplayHtmlFrame');
    iframe.setAttribute('sandbox', 'allow-same-origin allow-modals allow-popups allow-popups-to-escape-sandbox');
    iframe.setAttribute('referrerpolicy', 'no-referrer');
    iframe.setAttribute('title', title || getMessage.FTE14107 );
    iframe.addEventListener('load', () => { this.observeFrameHeight( iframe ); });
    iframe.srcdoc = this.buildDocument( html, title );
    return iframe;
}
// iframe の高さを中身に合わせる（内容・幅の変化にも追従する）。
observeFrameHeight( iframe ) {
    const win = iframe.contentWindow;
    const doc = iframe.contentDocument;
    if ( !win || !doc?.body ) return;
    const fit = () => {
        // documentElement はビューポート未満に縮まないため body で計測する（body は flow-root でマージン相殺を防いでいる）。
        const body = doc.body;
        const content = Math.max( body.scrollHeight, body.getBoundingClientRect().height );
        // 横スクロールバーが出ている場合はその分も加える。
        const scrollbar = Math.max( 0, win.innerHeight - doc.documentElement.clientHeight );
        const height = Math.ceil( content + scrollbar );
        if ( iframe.style.height !== `${height}px`) iframe.style.height = `${height}px`;
    };
    fit();
    iframe._resizeObserver?.disconnect();
    if ( typeof ResizeObserver === 'function') {
        iframe._resizeObserver = new ResizeObserver( fit );
        iframe._resizeObserver.observe( doc.body );
        iframe._resizeObserver.observe( iframe );
    }
}
/*
##################################################
   PDFダウンロード
##################################################
*/
// 表示内容をPDFとしてダウンロードする。
// 表示中の sandbox iframe をそのままブラウザの印刷（PDFに保存）に掛ける。
// 追加ライブラリ不要で、ベクターのまま出力でき文字も選択可能なPDFになる。
// button: クリックされたPDFボタン要素（同じ吹き出し内の iframe を辿る）。
printAsPdf( button ) {
    const inner = button?.closest?.('.aiAssistantChatDisplayHtmlInner');
    const iframe = inner?.querySelector?.('.aiAssistantChatDisplayHtmlFrame');
    const win = iframe?.contentWindow;
    if ( !win ) return;
    try {
        win.focus();
        win.print();
    } catch ( error ) {
        console.error('PDF出力（印刷）に失敗しました。', error );
    }
}

}
