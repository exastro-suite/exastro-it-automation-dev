////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / ai_assistant_chat.js
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
class AiAssistantChat {
/*
##################################################
   REST API URL
##################################################
*/
static get apiUrl() {
    const { organizationId, workspaceId } = fn.getCommonParams();
    return {
        // MCPサーバー（JSON-RPC）
        mcp: () => `/api/${organizationId}/workspaces/${workspaceId}/mcp`
    };
}
/*
##################################################
   Constructor
##################################################
*/
constructor( params, option ) {
    this.params = params;
    this.option = option;
}

/*
##################################################
    Mount
##################################################
*/
async mount( parentElement ) {
    // Main HTML build
    this.el = this.build();
    parentElement.appendChild(this.el);

    // 初期化
    await this.init();

    return;
}
/*
##################################################
    Destroy
##################################################
*/
destroy() {
    this.ac?.abort();
    // 画像プレビュー用の objectURL を解放してからDOMを破棄する。
    this.revokeAttachmentPreviews();
    this.el?.remove();
    this.ac = null;
    this.el = null;
}
/*
##################################################
    初期化
##################################################
*/
// 初期化の失敗は性質で2つに分けて扱う。
//   ・画面が成立しないもの（ユーザID・markdownit・DOM構築）… catchせず呼び出し元へ投げる。
//     ui.js側でエラーページへ遷移させるため、ここで握りつぶさない。
//   ・一部の機能が使えなくなるだけのもの（MCP・AI利用設定の取得）… 理由を保持して続行し、
//     新規チャット画面に通知として表示する（設定を直せば使える状態のため）。
async init() {
    // 画面が成立しない処理（失敗時はthrowする）
    this.initVariable();
    this.initMarkdownit();
    // 設定ダイアログを閉じたら、設定と認証状態を読み直して画面へ反映する
    this.setting = new AiAssistantSetting( this.params, {
        onClose: () => this.reloadSetting()
    });

    // 先に画面の枠を作る（このあとの取得が失敗しても、フッターと通知は表示できる）
    this.refElements();
    this.setFooterElement();
    this.bindEvents();

    // 縮退運転できる処理。片方の失敗でもう片方の結果を捨てない（＆未処理の例外に
    // ならない）ようにallSettledで待ち、失敗した理由はそれぞれ別に保持する。
    const [ mcp ] = await Promise.allSettled([
        this.initMcp(),
        this.loadSetting()
    ]);
    if ( mcp.status === 'rejected') {
        console.error( mcp.reason );
        this.mcpError = 'ITAの操作に使用するツールの一覧を取得できませんでした。<br>'
            + 'このままでもAIとの会話はできますが、AIアシスタントからITAを操作することはできません。<br>'
            + fn.escape( this.formatErrorMessage( mcp.reason ) );
    }

    // 画面専用ツールを登録する（MCPサーバー側のツール一覧が取れなくても使えるため、
    // 取得の成否にかかわらず登録して、選択肢の提示などはできる状態にしておく）
    this.initUiTools();

    this.updateFooter();

    // チャットスタート
    // （awaitして、画面を組み立てられなかった場合のエラーを呼び出し元まで伝える。
    //   会話を開始できなかった場合はnewChatStartの中で本文に表示する）
    await this.newChatStart();
}
// 要素参照
refElements() {
    this.elements = {
        header: this.el.querySelector('.aiAssistantHeader'),
        body: this.el.querySelector('.aiAssistantBody'),
        bodyInner: this.el.querySelector('.aiAssistantBodyInner'),
        footer: this.el.querySelector('.aiAssistantFooterInner'),

        // ボタン
        settingButton: this.el.querySelector('.aiAssistantSettingButton'),
        newChatButton: this.el.querySelector('.aiAssistantNewChatButton'),
        closeChatButton: this.el.querySelector('.aiAssistantCloseChatButton')
    };
}
// 変数設定
initVariable() {
    // LLM（新規チャットの開始時に作成する。AIサービス未設定・認証エラー時はnull）
    this.llm = null;
    // チャットで使用中のモデル（フッターで切り替える。既定はAI利用設定の既定のモデル）
    this.modelId = '';
    // AIサービスの認証確認の結果
    //   checked … 確認を実行したか（AIサービス未設定の場合は確認しない）
    //   valid   … 認証が通ったか
    //   message … 認証が通らなかった理由（画面に表示する）
    this.auth = { checked: false, valid: false, message: ''};
    // 初期化のうち、失敗しても画面は表示できる処理のエラー内容（新規チャット画面に表示する）
    //   mcpError     … MCPツール一覧の取得に失敗（ITAの操作ができない）
    //   settingError … AI利用設定の読み込みに失敗（チャットを開始できない）
    this.mcpError = '';
    this.settingError = '';
    // MCP（ツール一覧はinitMcpで取得する。取得に失敗した場合は空のまま）
    this.mcp = { tools: [], idCounter: 0 };
    // 作業中フラグ
    this.isRunning = false;
    // チャットID
    this.chatIdCounter = 0;
    // 履歴保存用クエリ
    this.historyQueues = new Map();
    // 添付したファイル
    this.files = [];
    // 添付画像のライブプレビュー用に生成した objectURL の控え。
    // 新規チャット／履歴復元で吹き出しを破棄する際にまとめて revoke する。
    this._attachmentPreviewUrls = [];
    this.uiTools = [];
    this.pendingChoiceToolId = null;
    // モデルのフォーマット崩れで、1応答に選択肢（ask_user_choice）の tool_use が複数
    // 出る（1つの選択肢が1 tool_use に分裂する等）ことがある。これらを1つの選択肢UIに
    // 統合したうえで、代表以外の余分な tool_use_id も未応答にならないよう保持しておく。
    this.pendingExtraChoiceToolIds = [];
    // 選択肢（ask_user_choice）と通常ツールが同じ応答に混在した場合、
    // 先に実行した通常ツールの tool_result を保持しておき、ユーザーが選択肢に
    // 回答したときに選択肢の tool_result とまとめて返すためのバッファ。
    this.pendingToolResults = [];
    // このターンで更新された ITA メニュー（menu_name_rest → 表示情報）。
    // maintenance-all / create-menu が成功するたびにここへ集約し、応答が完了した
    // タイミングで「更新されたページ」への（別タブで開く）リンクとしてまとめて表示する。
    this._turnUpdatedMenus = new Map();
    // メニューの主キー列 REST 名（pk_column_name_rest）のキャッシュ（絞り込みフィルター用）。
    this._menuPkRestCache = new Map();
    // イベント停止用
    this.ac = new AbortController();
    // ユーザID
    this.id = this.params?.user?.user_id ?? null; 
    if ( this.id === null ) {
        throw new Error('ユーザIDの取得に失敗しました。');
    }
}
// Markdown-it
initMarkdownit() {
    if ( typeof markdownit === 'function') {
        this.md = markdownit({
            breaks: true, // 単一の改行(\n)を<br>に変換する
            linkify: true, // http(s):// で始まる文字列を自動的にリンク化する
            highlight: function (str, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return '<pre><code class="hljs">' +
                            hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
                        '</code></pre>';
                    } catch (__) {}
                }
                return ''; // use external default escaping
            }
        });

        // リンクは別タブで開く（target="_blank" + rel を付与する）
        const defaultLinkOpen = this.md.renderer.rules.link_open
            || function ( tokens, idx, options, env, self ) {
                return self.renderToken( tokens, idx, options );
            };
        this.md.renderer.rules.link_open = function ( tokens, idx, options, env, self ) {
            const token = tokens[ idx ];
            token.attrSet( 'target', '_blank' );
            token.attrSet( 'rel', 'noopener noreferrer' );
            return defaultLinkOpen( tokens, idx, options, env, self );
        };
    } else {
        throw new Error('スクリプトの読み込みに失敗しました。（markdownit）');
    }
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   MCP
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    初期化
##################################################
*/
// MCPの状態（this.mcp）はinitVariableで用意しておく。ツール一覧の取得に失敗しても
// 画面専用ツールの登録などで参照するため、ここでは作り直さない。
async initMcp() {
    // initialize（サーバーはステートレスなのでセッションIDは返らないが、
    // MCPの作法として最初に呼んでおく）
    await this.mcpRequest('initialize');

    // 利用可能なツール一覧を取得する（権限で絞られた結果が返る）
    const result = await this.mcpRequest('tools/list');
    this.mcp.tools = result.tools ?? [];

    return;
}
/*
##################################################
    画面専用ツールの登録
##################################################
*/
// 画面専用ツール（MCPサーバーではなく画面側で実行するツール）のクラス一覧。
// ツールごとに「ツール定義（LLMへ渡す内容）」と「動作」を1ファイルにまとめている。
// ここに追加すれば、LLMへのツール登録・実行・履歴復元の振り分けまで自動で行われる。
static get uiToolClasses() {
    return [
        AiAssistantToolAskUserChoice,
        AiAssistantToolDisplayHtml
    ];
}
initUiTools() {
    this.uiToolMap = new Map();
    for ( const ToolClass of AiAssistantChat.uiToolClasses ) {
        this.uiToolMap.set( ToolClass.toolName, new ToolClass( this ) );
        // LLMへ渡すツール一覧に加える（MCPのツールと同じ形式で登録する）
        this.mcp.tools.push( ToolClass.definition );
    }
    // 画面専用ツールの名前一覧（応答ループでMCPツールと振り分けるために使う）
    this.uiTools = Array.from( this.uiToolMap.keys() );
}
// 画面専用ツールのインスタンスを取得する（未登録・MCPツールの場合はnull）
uiTool( name ) {
    return this.uiToolMap?.get( name ) ?? null;
}
/*
##################################################
    画面専用ツールへの委譲
##################################################
*/
// 画面専用ツールの処理は各ツールのファイル（ai_assistant/tools/）が持つ。
// チャット側からは以下のメソッドを窓口として呼び出す。
// 画面専用ツールのうち、ユーザーの選択・回答を待つ種類（ask_user_choice）かどうかを判定する。
// display_html のような即時表示ツールと処理を分けるために使う。
isUiChoiceTool( name ) {
    return name === AiAssistantToolAskUserChoice.toolName;
}
// 選択肢を表示してユーザーの回答を待つ（tool_result は次の送信で返す）
askUserChoice( toolUse ) {
    return this.uiTool( AiAssistantToolAskUserChoice.toolName )?.execute( toolUse ) ?? null;
}
// 選択肢の1件を { label, action } 形式に正規化する
normalizeChoiceOption( opt ) {
    return this.uiTool( AiAssistantToolAskUserChoice.toolName )?.normalizeOption( opt )
        ?? { label: String( opt ?? ''), action: 'other'};
}
// 選択肢の応答（tool_use ブロック群）がフォーマット崩れかどうかを判定する
isChoiceResponseMalformed( choiceBlocks ) {
    return this.uiTool( AiAssistantToolAskUserChoice.toolName )?.isMalformed( choiceBlocks ) ?? false;
}
// 分裂した複数の選択肢 tool_use を1つの選択肢 tool_use に統合する
mergeChoiceBlocks( blocks ) {
    return this.uiTool( AiAssistantToolAskUserChoice.toolName )?.mergeBlocks( blocks )
        ?? { id: '', _extraIds: [], arguments: { question: '', options: []}};
}
// display_html の表示内容をPDFとしてダウンロードする（吹き出しのPDFボタンから呼ばれる）
printDisplayHtmlAsPdf( button ) {
    this.uiTool( AiAssistantToolDisplayHtml.toolName )?.printAsPdf( button );
}
/*
##################################################
    MCPサーバーへJSON-RPCリクエストを送信する
##################################################
*/
async mcpRequest( method, params = {} ) {
    const token = this.getToken();
    const response = await fetch( AiAssistantChat.apiUrl.mcp(), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: method,
            params: params,
            id: ++this.mcp.idCounter
        })
    });

    // JSON-RPCのエラーはHTTP 400/404/500でも本文にerrorが入る
    const json = await response.json().catch( () => null );
    if ( json?.error ) {
        throw new Error(`MCP error (${json.error.code}): ${json.error.message}`);
    }
    if ( !response.ok ) {
        throw new Error(`MCP request failed: ${response.status}`);
    }
    return json.result;
}
/*
##################################################
    MCPツールを呼び出す
##################################################
*/
async mcpToolCall( name, args = {} ) {
    const result = await this.mcpRequest('tools/call', { name: name, arguments: args });

    // ツール実行失敗はHTTP 200 + isError:true で返るため、ここで判定する
    if ( result.isError ) {
        const text = result.content?.map( c => c.text ).join('\n') ?? 'tool call failed';
        throw new Error( text );
    }
    return result;
}
/*
##################################################
    LLMが要求したツールを実行する
##################################################
*/
// LLMの tool_use ブロックを受け取ってMCPサーバーのツールを実行し、tool_result を返す。
// ・応答（JSON-RPCのエンベロープ）はそのまま tool_result の content に載せてLLMへ渡す
// ・ドライバー実行系のツールは、完了まで進捗を監視してから結果を返す
// runningEl … 「ツール実行中」の吹き出し（進捗表示に使う）
// signal    … 停止用のAbortSignal（MCPへのリクエストと進捗監視をまとめて中断する）
async executeTool( toolUse, runningEl = null, signal = null ) {
    toolUse.name = toolUse.name ?? toolUse.params?.name;
    try {
        const toolResponse = await AiAssistantChat.fetchWithRetry( AiAssistantChat.apiUrl.mcp(), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getToken()}`
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                id: ++this.mcp.idCounter,
                method: 'tools/call',
                params: {
                    name: toolUse.name,
                    arguments: toolUse.arguments ?? toolUse.input ?? {}
                }
            }),
            signal
        });
        const toolResult = await toolResponse.json();

        // ドライバー実行系ツールなら進捗を購読して実行状況を表示し、
        // 確定した最終ステータスを取得する（完了まで待機）
        const progressOutcome = await this.watchDriverProgress( toolUse, toolResult, runningEl );

        // 最終ステータスが取れた場合は tool_result に反映する。
        // execute-driver の即時レスポンス（「実行を開始しました」）だけだと
        // LLMが開始で会話を締めてしまう / 逆に自分でステータス確認を繰り返して
        // execute-driver を再実行してしまうため、進捗監視の確定結果と
        // 「次に取るべき行動」を明示的に指示する。
        let resultForLlm = toolResult;
        if ( progressOutcome ) {
            if ( progressOutcome.type === 'done') {
                resultForLlm = {
                    ...toolResult,
                    driver_execution: {
                        monitored_by_server: true,
                        completed: true,
                        final_status: progressOutcome.status ?? '',
                        status_detail: progressOutcome.result ?? null,
                        // LLMへの明示指示（再実行・再確認ループを防ぐ）
                        instruction: `この実行はサーバ側で完了まで監視され、最終ステータス「${progressOutcome.status ?? ''}」で終了済みです。execute-driver / dryrun-driver / get-driver-status を再度呼び出さず、この最終ステータスをユーザーに報告して会話を終えてください。`
                    }
                };
            } else {
                resultForLlm = {
                    ...toolResult,
                    driver_execution: {
                        monitored_by_server: true,
                        completed: false,
                        reason: progressOutcome.type,
                        message: progressOutcome.message ?? '',
                        // 未完了でも自動リトライ（再実行）はさせない
                        instruction: `サーバ側の進捗監視が最終ステータスに到達する前に終了しました（理由: ${progressOutcome.type}）。実行自体は開始済みのため、execute-driver / dryrun-driver を再実行してはいけません。状況をユーザーに報告し、必要なら手動での状況確認を促してください。`
                    }
                };
            }
        }

        // maintenance-all / create-menu で ITA のページ（メニュー）が更新された場合、
        // 応答完了時にリンクを出せるよう、更新先メニューをこのターン分として控えておく。
        this.collectUpdatedMenu( toolUse, toolResult );

        return {
            type: 'tool_result',
            tool_use_id: toolUse.id ?? '',
            content: JSON.stringify( resultForLlm )
        };
    } catch ( error ) {
        // ユーザ都合の停止（AbortError）は tool_result を返さず再スローし、
        // 呼び出し側でターンごと巻き戻す（未応答 tool_use を残さない）。
        if ( error?.name === 'AbortError' || signal?.aborted ) {
            throw error;
        }
        // エラーでも内容をLLMに渡すため処理を止めない。
        // tool_use に対応する user ターンは必ず tool_use_id 付きの tool_result で
        // 始まる必要があるため、type / tool_use_id を欠かさず、is_error で失敗を伝える。
        return {
            type: 'tool_result',
            tool_use_id: toolUse.id ?? '',
            is_error: true,
            content: fn.jsonStringify( error )
        };
    }
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   更新された ITA ページのリンク
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    更新されたページの収集
##################################################
*/
// ITA のページ（メニュー）を更新するツールの一覧。
// 値は toolUse.arguments から menu_name_rest / 表示名を取り出す関数。
static get UPDATE_MENU_TOOLS() {
    return {
        // レコードの登録/更新/廃止/復活/削除。arguments.menu が menu_name_rest。
        'maintenance-all': ( args ) => ({
            menuNameRest: args?.menu ?? '',
            label: args?.menu ?? ''
        }),
        // メニュー（パラメータシート）作成。menu_definition.menu に定義が入る。
        'create-menu': ( args ) => ({
            menuNameRest: args?.menu_definition?.menu?.menu_name_rest ?? '',
            label: args?.menu_definition?.menu?.menu_name ?? args?.menu_definition?.menu?.menu_name_rest ?? ''
        })
    };
}
// 更新先メニューを（menu_name_rest をキーに）このターン分として控える共通処理。
// 同一メニューへの複数操作は1リンクに集約する（表示名・IDリストは後勝ちで更新）。
// idList: maintenance-all で登録・更新されたレコードの uuid 群（絞り込み用、無ければ空）。
_addUpdatedMenu( name, args, idList = [] ) {
    const extractor = AiAssistantChat.UPDATE_MENU_TOOLS[ name ];
    if ( !extractor ) return;
    const { menuNameRest, label } = extractor( args ?? {} );
    if ( !menuNameRest ) return;
    if ( !( this._turnUpdatedMenus instanceof Map ) ) this._turnUpdatedMenus = new Map();
    this._turnUpdatedMenus.set( menuNameRest, {
        menuNameRest,
        label: label || menuNameRest,
        idList: Array.isArray( idList ) ? idList : []
    });
}
// tool_result（JSON-RPC の structuredContent 等）から登録・更新レコードの uuid 群を取り出す。
// ITA の maintenance/all 応答は `IdList` に uuid の配列を返す（menu_maintenance_all.py 準拠）。
// エンベロープの深さがゆらぐため、IdList を再帰探索する。
_extractIdList( node, depth = 0 ) {
    if ( depth > 6 || !node || typeof node !== 'object') return [];
    if ( Array.isArray( node.IdList ) ) {
        return node.IdList.filter(( id ) => typeof id === 'string' && id );
    }
    for ( const val of Object.values( node ) ) {
        if ( val && typeof val === 'object') {
            const found = this._extractIdList( val, depth + 1 );
            if ( found.length ) return found;
        }
    }
    return [];
}
// ツール実行結果（ライブ）が ITA ページの更新なら、更新先メニューを控える。
// エラー応答（isError）や menu_name_rest 不明のものは対象外。
collectUpdatedMenu( toolUse, toolResult ) {
    const name = toolUse?.name ?? '';
    if ( !AiAssistantChat.UPDATE_MENU_TOOLS[ name ] ) return;

    // ツール自体がエラーを返した場合は更新扱いにしない。
    const structured = toolResult?.result?.structuredContent ?? {};
    if ( structured.isError === true || toolResult?.result?.isError === true ) return;

    this._addUpdatedMenu( name, toolUse.arguments ?? toolUse.input, this._extractIdList( structured ) );
}
// 履歴（保存済み tool_use / tool_result）から更新先メニューを控える（再開時用）。
// tool_result.content は executeTool で JSON文字列化されているためパースして判定する。
collectUpdatedMenuFromHistory( toolUse, toolResult ) {
    const name = toolUse?.name ?? '';
    if ( !AiAssistantChat.UPDATE_MENU_TOOLS[ name ] ) return;

    // エラーで終わった実行はリンク対象外。
    if ( toolResult?.is_error === true ) return;
    let parsed = toolResult?.content ?? null;
    if ( typeof parsed === 'string') {
        try { parsed = JSON.parse( parsed ); } catch ( error ) { parsed = null; }
    }
    const structured = parsed?.result?.structuredContent ?? {};
    if ( structured.isError === true || parsed?.result?.isError === true ) return;

    this._addUpdatedMenu( name, toolUse.arguments ?? toolUse.input, this._extractIdList( structured ) );
}
/*
##################################################
    更新されたページのリンク表示
##################################################
*/
// メニューの主キー列 REST 名（pk_column_name_rest）を取得する。
// 絞り込みフィルターのキー（uuid 相当。メニューにより名称が異なる）に使う。
// 一度取得したらキャッシュし、取得失敗時は null。
async getMenuPkRest( menuNameRest ) {
    if ( !( this._menuPkRestCache instanceof Map ) ) this._menuPkRestCache = new Map();
    if ( this._menuPkRestCache.has( menuNameRest ) ) return this._menuPkRestCache.get( menuNameRest );
    let pkRest = null;
    try {
        const info = await fn.fetch(`/menu/${menuNameRest}/info/`);
        pkRest = info?.menu_info?.pk_column_name_rest ?? null;
    } catch ( error ) {
        console.warn('getMenuPkRest: メニュー情報の取得に失敗しました', menuNameRest, error );
    }
    this._menuPkRestCache.set( menuNameRest, pkRest );
    return pkRest;
}
// ITA メニューページのURLを組み立てる（別タブ表示用）。
// ITA本体（トップ画面）は ?menu=<menu_name_rest> でメニューを切り替えるため、
// 現在のトップ画面のパスに menu パラメータを付与した絶対URLを返す。
// filter を渡すと ITA のフィルター形式（{ 列: { LIST: [...] } }）を &filter= に付与する。
buildMenuUrl( menuNameRest, filter = null ) {
    const base = `${top.location.origin}${top.location.pathname}`;
    let url = `${base}?menu=${encodeURIComponent( menuNameRest )}`;
    if ( filter ) {
        // fn.filterEncode = encodeURIComponent( JSON.stringify( filter ) )
        url += `&filter=${fn.filterEncode( filter )}`;
    }
    return url;
}
// このターンで更新された ITA ページへのリンクをまとめて1つの吹き出しで表示する。
// 表示後は控えをクリアし、同じリンクを次のセグメントで重複表示しないようにする。
renderUpdatedMenuLinks( scroll = true ) {
    const menus = ( this._turnUpdatedMenus instanceof Map ) ? this._turnUpdatedMenus : null;
    if ( !menus || !menus.size || !this.elements.chatList ) return;
    this._turnUpdatedMenus = new Map();

    const el = document.createElement('li');
    el.classList.add('aiAssistantChatItem', 'aiAssistantChatAssistantMessage', 'aiAssistantChatUpdatedMenus');
    // 直前がアシスタントなら連続クラスを付与
    const prevItem = this.elements.chatList.lastElementChild;
    if ( prevItem?.classList.contains('aiAssistantChatAssistantMessage') ) {
        el.classList.add('aiAssistantChatAssistantMessageChain');
    }

    const inner = document.createElement('div');
    inner.classList.add('aiAssistantChatItemInner', 'aiAssistantChatAssistantMessageInner');

    const list = document.createElement('ul');
    list.classList.add('aiAssistantUpdatedMenusList');
    for ( const { menuNameRest, label, idList } of menus.values() ) {
        const item = document.createElement('li');
        item.classList.add('aiAssistantUpdatedMenusItem');

        const a = document.createElement('a');
        a.classList.add('aiAssistantUpdatedMenusLink');
        // まずはフィルター無しの基本URLを設定しておく（主キー取得失敗時のフォールバック）。
        a.href = this.buildMenuUrl( menuNameRest );
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.innerText = label || menuNameRest;
        item.append( a );
        list.append( item );

        // 登録・更新レコードがあれば、主キー列名を取得して該当レコードのみ絞り込む
        // フィルターを URL に埋め込む（非同期。取得できたら href を差し替える）。
        if ( Array.isArray( idList ) && idList.length ) {
            this.getMenuPkRest( menuNameRest ).then(( pkRest ) => {
                if ( !pkRest ) return;
                // discard: { NORMAL: '' } を付けないと ITA 既定で廃止レコードが除外され、
                // 廃止したレコードに絞り込んでもヒットしないため明示的に「廃止含む」を指定する。
                const filter = { [ pkRest ]: { LIST: idList }, discard: { NORMAL: ''}};
                a.href = this.buildMenuUrl( menuNameRest, filter );
                a.classList.add('aiAssistantUpdatedMenusLinkFiltered');
                a.title = `更新した ${idList.length} 件に絞り込んで開きます`;
            });
        }
    }
    inner.append( list );
    el.append( inner );

    // 回答待ちの選択肢が表示中なら、その直前に挿入する。
    // （選択肢は updateChat 側で常に末尾へ寄せる作りのため、リンクを末尾に足すと
    //   選択肢より後ろに来てしまう。選択肢を一番最後に保つため前に差し込む）
    const choiceItem = this.elements.chatList.querySelector('.aiAssistantChatUserChoice');
    if ( choiceItem ) {
        this.elements.chatList.insertBefore( el, choiceItem );
    } else {
        this.elements.chatList.append( el );
    }
    if ( scroll ) setTimeout( () => this.scrollChatArea( el ), 100 );
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   状態チェック
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    AIアシスタントが設定済みかチェックする
##################################################
*/
// assistantCheck = true : LLMのみチェックする
checkAiAssistantSetting( assistantCheck = false) {
    return AiAssistantSetting.isConfigured( this.setting.preference, assistantCheck );
}
/*
##################################################
    AIサービスの認証が通るかチェックする
##################################################
*/
// 設定されていても、認証情報の期限切れや失効でチャットを開始できないことがある。
// 設定を読み込んだ直後に確認して、通らなかった場合は再設定を促すため結果を保持する。
async checkAiAssistantAuth() {
    this.auth = { checked: false, valid: false, message: ''};

    // AIサービスが未設定の場合は確認する認証情報がない
    if ( !this.checkAiAssistantSetting( true ) ) return this.auth;

    try {
        const result = await this.setting.verifyCredential( this.setting.preference.ai_service_id );
        this.auth = {
            checked: true,
            valid: result?.valid === true,
            message: ( result?.valid === true )? '': result?.message ?? ''
        };
    } catch ( error ) {
        // 確認そのものに失敗した場合も、チャットは開始できないため認証エラーとして扱う
        console.error( error );
        this.auth = { checked: true, valid: false, message: error?.message ?? ''};
    }
    return this.auth;
}
/*
##################################################
    AI利用設定の読み込み
##################################################
*/
// AI利用設定を読み込み、その認証情報で実際に認証できるかを確認する。
// 取得に失敗しても画面自体は表示できるため、理由を保持して続行する（未設定と同じ扱いに
// なり、チャットは開始できない状態で「読み込めなかったこと」を本文へ表示する）。
// 一時的な失敗であれば、設定ダイアログを閉じたタイミングの再読み込みで回復する。
async loadSetting() {
    this.settingError = '';
    try {
        await this.setting.loadPreference();
    } catch ( error ) {
        console.error( error );
        this.settingError = 'AI利用設定を読み込めませんでした。<br>'
            + fn.escape( this.formatErrorMessage( error ) );
    }
    await this.checkAiAssistantAuth();
    return;
}
/*
##################################################
    チャットを開始できるかチェックする
##################################################
*/
// 設定が完了していて、かつその認証情報で認証が通っている状態
isChatReady() {
    return this.checkAiAssistantSetting() && this.auth.valid;
}
// 設定はされているが認証が通らなかった状態
isAuthError() {
    return this.checkAiAssistantSetting( true ) && this.auth.checked && !this.auth.valid;
}
/*
##################################################
    設定ダイアログを閉じたあとの再読み込み
##################################################
*/
// 認証情報やモデルを再設定した結果を反映する
// （初期化時にAI利用設定を読み込めていない場合は、ここで読み込み直す）
async reloadSetting() {
    if ( this.settingError ) {
        await this.loadSetting();
    } else {
        await this.checkAiAssistantAuth();
    }

    // 新規チャット画面のみ作り直す（チャット中は表示を維持し、フッターだけ更新する）
    if ( this.newChat ) {
        await this.newChatStart();
    } else {
        this.updateFooter();
    }
    return;
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   基本UI
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    Main HTML
##################################################
*/
build() {
    const el = document.createElement('div');
    el.className = 'aiAssistantContainer';
    el.innerHTML = `
    <div class="aiAssistantContainerInner">
        <div class="aiAssistantHeader">${this.createHeaderMenuHtml()}</div>
        <div class="aiAssistantBody">
            <div class="aiAssistantBodyInner">
            </div>
        </div>
        <div class="aiAssistantFooter">
            <div class="aiAssistantFooterInner">
            </div>
        </div>
    </div>`;
    return el;
}
/*
##################################################
    Header HTML
##################################################
*/
createHeaderMenuHtml() {
    const menuList = {
        Main: [
            { button: { className: 'aiAssistantNewChatButton', icon: 'edit', text: '新しいチャット', type: 'newChat', action: 'positive', minWidth: '160px', disabled: false }},
            { button: { className: 'aiAssistantCloseChatButton', icon: 'check', text: 'チャット終了', type: 'closeChat', action: 'positive', minWidth: '160px', disabled: true }}
        ],
        Sub: [
            { button: { className: 'aiAssistantSettingButton', icon: 'gear', text: 'AIアシスタント設定', type: 'aiAssistantSetting', action: 'default', minWidth: '160px'}}
        ]
    };
    return fn.html.operationMenu( menuList );
}
/*
##################################################
    Footer HTML
##################################################
*/
// Footer HTML
setFooterElement() {
    this.elements.footer.append( this.createFooterAiNameElement() );
    this.elements.footer.append( this.createFooterModelListElement() );
}
// 共通HTML
createFooterCommonElement() {
    const el = document.createElement('div');
    el.classList.add('aiAssistantFooterBlock')
    el.innerHTML = `
    <dl class="aiAssistantFooterList">
        <dt class="aiAssistantFooterTitle"></dt>
        <dd class="aiAssistantFooterItem"></dd>
    </dl>`;
    return el;
}
// 共通テキスト
setFooterCommonText( element, text ) {
    element.innerHTML = `<span class="aiAssistantFooterText">${text}</span>`;
}
// AI名HTML
createFooterAiNameElement() {
    const el = this.createFooterCommonElement();
    this.setFooterCommonText( el.querySelector('.aiAssistantFooterTitle'), 'AI');
    this.elements.aiName = el.querySelector('.aiAssistantFooterItem');
    return el;
}
// モデルリストHTML
createFooterModelListElement() {
    const el = this.createFooterCommonElement();
    this.setFooterCommonText( el.querySelector('.aiAssistantFooterTitle'), 'モデル');
    this.elements.modelList = el.querySelector('.aiAssistantFooterItem');
    return el;
}
// AI名更新
updateFooterAiName() {
    const aiName = ( this.checkAiAssistantSetting( true ) )
        ? fn.escape( this.setting.currentServiceName ): '<span class="notSelected">未選択</span>';
    this.setFooterCommonText( this.elements.aiName, aiName );
}
// Footer 更新
updateFooter() {
    this.updateFooterAiName();
    this.updateFooterModelList();
}
// モデルリスト更新
// AI利用設定のピックアップモデルを、チャット中に切り替えられる選択肢として表示する
updateFooterModelList() {
    const selectedList = ( this.checkAiAssistantSetting() )? this.setting.currentPickupModels: [];
    if ( !selectedList.length ) {
        this.modelId = '';
        this.setFooterCommonText( this.elements.modelList, '<span class="notSelected">未選択</span>');
        return;
    }

    // 使用中のモデルが選択肢から外れた場合（設定変更・AIサービス切り替え）は、既定のモデルへ戻す
    const selectModelId = this.getUseModelId( selectedList );
    this.modelId = selectModelId;

    const modelSelectWrap = document.createElement('div');
    modelSelectWrap.classList.add('modelSelectWrap');

    const modelSelectedName = document.createElement('div');
    modelSelectedName.classList.add('modelSelectedName');
    modelSelectedName.innerText = selectedList.find(( item ) => item.id === selectModelId )?.name ?? '';

    const modelList = document.createElement('ul');
    const name = `modelSelectRadio`;
    modelList.classList.add('modelSelectList');
    // モデルIDには記号が含まれるため、id属性には連番を使う
    selectedList.forEach(( item, index ) => {
        const modelid = item.id ?? '';
        const modelItem = document.createElement('li');
        modelItem.classList.add('modelSelectItem');

        const modelItemLabel = document.createElement('label');
        modelItemLabel.classList.add('modelSelectLabel');
        modelItemLabel.setAttribute('for', `modelSelectRadio_${index}`)
        modelItemLabel.innerText = item.name ?? '';

        const modelItemRadio = document.createElement('input');
        modelItemRadio.classList.add('modelSelectRadio');
        modelItemRadio.setAttribute('type', 'radio');
        modelItemRadio.setAttribute('name', name );
        modelItemRadio.setAttribute('id', `modelSelectRadio_${index}`);
        modelItemRadio.setAttribute('value', modelid );
        if ( selectModelId === modelid ) {
            modelItemRadio.checked = true;
        }

        modelItem.append( modelItemRadio, modelItemLabel );
        modelList.appendChild( modelItem );
    });
    modelSelectWrap.append( modelSelectedName, modelList );

    // 幅を最長モデル名に合わせるための採寸用（非表示）要素
    const modelSelectSizer = document.createElement('div');
    modelSelectSizer.classList.add('modelSelectSizer');
    modelSelectSizer.setAttribute('aria-hidden', 'true');
    for ( const item of selectedList ) {
        const sizerItem = document.createElement('div');
        sizerItem.classList.add('modelSelectSizerItem');
        sizerItem.innerText = item.name ?? '';
        modelSelectSizer.appendChild( sizerItem );
    }
    modelSelectWrap.append( modelSelectSizer );

    this.elements.modelList.replaceChildren( modelSelectWrap );
}
// チャットで使用するモデル（切り替えたモデルを優先し、選択肢になければ既定のモデル）
getUseModelId( modelList = this.setting.currentPickupModels ) {
    const has = ( modelId ) => Boolean( modelId ) && modelList.some(( item ) => item.id === modelId );
    if ( has( this.modelId ) ) return this.modelId;
    if ( has( this.setting.currentModelId ) ) return this.setting.currentModelId;
    return modelList[0]?.id ?? '';
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Chat
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    新規チャット画面
##################################################
*/
async newChatStart() {
    // 新しい会話を始めるので、前の会話のLLM（会話履歴）は破棄する
    this.llm = null;
    this.setNewChat();

    try {
        await this.ensureLlm();
    } catch ( error ) {
        // 準備に失敗した場合は、その旨を表示する（送信時に再度用意を試みる）
        console.error( error );
        this.elements.chatBody?.append(
            this.createNoticeMessageElement(
                '会話を開始できませんでした。<br>' + fn.escape( this.formatErrorMessage( error ) )
            )
        );
    }
}
// LLM層を用意する。用意済みならそれを返す。
//   AIサービスが未設定、または認証が通っていない場合はnullを返す
//   （フッターと本文に設定を促すメッセージを表示している状態）
// AIサービス側の会話（履歴の保存先）は、最初の送信・保存のときにLLM層が作成する
// （画面を開くだけで空の会話が会話履歴に残らないようにするため）。
async ensureLlm() {
    if ( this.llm ) return this.llm;
    if ( !this.isChatReady() ) return null;

    // 使用するモデルはフッターで切り替えたものを優先する（未選択ならAI利用設定の既定のモデル）
    this.modelId = this.getUseModelId();

    // システムプロンプトとツールの実行結果の解釈はAIサービス側（プラットフォームAPI）が
    // 持つため、ここではAIサービス・モデルとツール一覧のみを渡す。
    const llm = new AiAssistantLlm();
    await llm.setup({
        aiServiceId: this.setting.currentAiServiceId,
        modelId: this.modelId
    }, this.mcp.tools );

    this.llm = llm;
    return this.llm;
}
// チャット画面
setNewChat() {
    // メッセージ初期化
    this.newChat = true;
    this.chatId = this.chatIdCounter++;
    // 新しい会話を始めるので、中断再開マーカーは破棄する（前の会話を自動再開しない）。
    this._clearActiveChat();
    this.clearFile();
    // 破棄する吹き出しの画像プレビュー（objectURL）を解放する。
    this.revokeAttachmentPreviews();

    // 初期チャットエリア作成
    const el = this.createChatContainerElement();
    this.elements.body.classList.remove('aiAssistantChatNow');
    this.elements.body.classList.add('aiAssistantNewChat');
    this.elements.chatBody = el.querySelector('.aiAssistantChatBody');
    // 挨拶
    this.elements.chatBody.append( this.createGreetingMessageElement() );
    // 初期化で一部が読み込めなかった場合（設定を直せば使える状態のため理由を表示する）
    if ( this.settingError ) {
        this.elements.chatBody.append( this.createNoticeMessageElement( this.settingError ) );
    } else if ( !this.isChatReady() ) {
        // 未設定・認証エラーの場合
        this.elements.chatBody.append( this.createNoticeMessageElement() );
    }
    if ( this.mcpError ) {
        this.elements.chatBody.append( this.createNoticeMessageElement( this.mcpError ) );
    }

    // 設定ボタンは新規チャット画面のみ
    this.elements.settingButton.disabled = false;

    // チャット閉じるボタン非活性
    this.elements.closeChatButton.disabled = true;

    this.elements.bodyInner.replaceChildren( el );
    this.updateFooter();
}
/*
##################################################
    Chat HTML
##################################################
*/
createChatContainerElement() {
    const el = document.createElement('div');
    el.classList.add('aiAssistantChatContainer');
    el.innerHTML = `
    <div class="aiAssistantChatInner">
        <div class="aiAssistantChatBody">
            <div class="aiAssistantCharacter">${fn.html.icon('ai_assistant')}</div>
        </div>
        <div class="aiAssistantChatFooter"></div>
    </div>`;
    // 準備完了している
    if ( this.isChatReady() ) {
        const footer = `
        <div class="aiAssistantChatComposer">
            <div class="aiAssistantInputSelectFiles">
                <ul class="aiAssistantInputSelectFilesList">
                </ul>
            </div>
            <div class="aiAssistantInputMessage">
                <textarea name="aiAssistantInputTextarea" class="aiAssistantInputTextarea" placeholder="ご用件を入力してください。"></textarea>
            </div>
            <div class="aiAssistantInputActions">
                ${fn.html.button( fn.html.icon('plus'), 'aiAssistantInputActionsFileButton itaButton button popup', { type: 'file', action: 'default  ', title: 'ファイル添付'})}
                ${fn.html.button( fn.html.icon('send'), 'aiAssistantInputActionsSendButton itaButton button popup', { type: 'send', action: 'positive', title: '送信'})}
                ${fn.html.button( fn.html.icon('stop'), 'aiAssistantInputActionsStopButton itaButton button popup', { type: 'stop', action: 'danger', title: '停止'})}
            </div>
        </div>
        ${this.createDisclaimerMessageHtml()}`;
        el.querySelector('.aiAssistantChatFooter').innerHTML = footer;
        this.elements.message = el.querySelector('.aiAssistantInputTextarea');
        this.elements.fileList = el.querySelector('.aiAssistantInputSelectFilesList');
        // 保持中のファイルを描画
        this.renderFileList();
    }
    return el;
}
// 挨拶
createGreetingMessageElement() {
    const el = document.createElement('div');
    el.classList.add('aiAssistantGreetingMessage');

    const hour = new Date().getHours();
    let message = '';
    if (hour >= 5 && hour < 11) {
        message += 'おはようございます。';
    } else if (hour >= 11 && hour < 17) {
        message += 'こんにちは。';
    } else if (hour >= 17 && hour < 22) {
        message += 'こんばんは。';
    } else {
        message += '遅い時間までお疲れさまです。';
    }
    message += 'Exastro AIアシスタントです。';

    if ( this.isChatReady() ) {
        message += '<br>どのようなお手伝いをしましょうか？';
    }

    el.innerHTML = message;
    return el;
}
// 未設定・認証エラー
//   html … 個別の通知内容（省略時は設定状況から判定して表示する）
createNoticeMessageElement( html ) {
    const el = document.createElement('div');
    el.classList.add('aiAssistantNoticeMessage');

    if ( html ) {
        el.innerHTML = fn.html.icon('circle_exclamation') + ' ' + html;
        return el;
    }

    // 認証が通らなかった場合は、認証情報の再設定を促す
    if ( this.isAuthError() ) {
        const serviceName = this.setting.currentServiceName;
        const detail = ( this.auth.message )
            ? `<div class="aiAssistantNoticeDetail">${fn.escape( this.auth.message )}</div>`: '';
        el.innerHTML = fn.html.icon('circle_exclamation')
            + ` AIサービス（${fn.escape( serviceName )}）の認証に失敗しました。`
            + '<br>認証情報の有効期限が切れている可能性があります。<br>「AIアシスタント設定」から認証情報を再設定してください。'
            + detail;
        return el;
    }

    el.innerHTML = fn.html.icon('circle_exclamation') + ' ご利用の準備が完了していません。<br>「AIアシスタント設定」から設定を完了してください。';
    return el;
}
// 免責事項
createDisclaimerMessageHtml() {
    return '<div class="aiAssistantDisclaimerMessage">AIの回答や操作結果は、正確性および完全性を保証するものではありません。AIアシスタントを通じた操作については、実行前に内容と影響範囲を確認し、実行後も結果が意図した状態になっていることをご確認ください。</div>';
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ファイル
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    ファイル選択
##################################################
*/
async fileSelect() {
    this.isRunning = true;

    try {
        // 複数ファイル選択
        const files = await new Promise(( resolve ) => {
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.addEventListener('change', () => {
                resolve( Array.from( input.files ?? [] ) );
            }, { once: true });
            // キャンセル時は空配列で解決
            input.addEventListener('cancel', () => {
                resolve( [] );
            }, { once: true });
            input.click();
        });

        if ( files.length ) {
            await this.setFile( files );
        }
    } catch ( error ) {
        console.error( error );
    }

    this.isRunning = false;
}
/*
##################################################
    ファイル準備
##################################################
*/
setFile( files, options = {} ) {
    // アップロードは送信時に行うため、ここではファイルを保持するだけ
    // useLlm : LLMにファイルを渡すか（デフォルトは渡さない）
    // options.useLlm : 追加時点で解析ONにするか（貼り付け画像などで使用）
    const useLlm = options.useLlm === true;
    if ( !Array.isArray( this.files ) ) this.files = [];
    this.files.push( ...files.map(( file ) => ({ file, useLlm })) );
    this.renderFileList();
}
// 貼り付けられた画像ファイルに、わかりやすく重複しないファイル名を付け直す。
// クリップボード由来の画像は名前が空だったり "image.png" 固定だったりするため、
// MIMEタイプから拡張子を決め、日時付きの名前にして一覧での区別をつける。
normalizePastedImageFile( file ) {
    // すでに拡張子付きの妥当な名前があればそのまま使う（"image.png" 等の既定名は付け替える）。
    const name = file.name ?? '';
    const hasProperName = name && name !== 'image.png' && /\.[^.]+$/.test( name );
    if ( hasProperName ) return file;

    const mimeType = file.type ?? '';
    const ext = ( mimeType.split('/')[ 1 ] || 'png').split('+')[ 0 ];
    const now = new Date();
    const pad = ( n ) => String( n ).padStart( 2, '0');
    const stamp = `${now.getFullYear()}${pad( now.getMonth() + 1 )}${pad( now.getDate() )}`
        + `_${pad( now.getHours() )}${pad( now.getMinutes() )}${pad( now.getSeconds() )}`;
    const newName = `pasted-image-${stamp}.${ext}`;

    // File 名は読み取り専用のため、同じ内容で名前だけ変えた File を作り直す。
    try {
        return new File( [ file ], newName, { type: mimeType, lastModified: file.lastModified });
    } catch ( error ) {
        // File コンストラクタが使えない環境では元のファイルをそのまま返す。
        console.warn('貼り付け画像のファイル名変更に失敗しました。', error );
        return file;
    }
}
// 指定したインデックスのファイルを削除する
removeFile( index ) {
    if ( !Array.isArray( this.files ) ) return;
    if ( index < 0 || index >= this.files.length ) return;
    this.files.splice( index, 1 );
    this.renderFileList();
}
// 指定したインデックスのテキストファイルをエディタで編集する
async editFile( index ) {
    if ( !Array.isArray( this.files ) ) return;
    if ( index < 0 || index >= this.files.length ) return;
    const item = this.files[ index ];
    const file = item.file;
    // common.js の fileEditor を利用（edit モードは編集結果を { name, file } で返す）
    const result = await fn.fileEditor( file, file.name, 'edit', {} );
    // インデックスが編集中にずれる可能性があるため対象を再取得して更新する
    const currentIndex = this.files.indexOf( item );
    if ( result && result.file && currentIndex !== -1 ) {
        this.files[ currentIndex ] = { ...item, file: result.file };
        this.renderFileList();
    }
}
// 指定したインデックスの画像ファイルをプレビュー表示する
async previewFile( index ) {
    if ( !Array.isArray( this.files ) ) return;
    if ( index < 0 || index >= this.files.length ) return;
    const file = this.files[ index ].file;
    await fn.fileEditor( file, file.name, 'preview', {} );
}
// 吹き出し内の画像サムネイルから、添付時と同じプレビュー（fn.fileEditor）を開く。
// 送信後はファイル実体を保持していないため、生成済みの objectURL から blob を
// 取り出して File を再構築し、プレビューに渡す。
async previewAttachment( url, filename ) {
    if ( !url ) return;
    try {
        const res = await fetch( url );
        const blob = await res.blob();
        const name = filename || 'image';
        const file = new File( [ blob ], name, { type: blob.type });
        await fn.fileEditor( file, name, 'preview', {} );
    } catch ( error ) {
        console.error('プレビューの表示に失敗しました。', error );
    }
}
// 指定したインデックスのファイルのLLM送信フラグを切り替える
toggleFileLlm( index ) {
    if ( !Array.isArray( this.files ) ) return;
    if ( index < 0 || index >= this.files.length ) return;
    this.files[ index ].useLlm = !this.files[ index ].useLlm;
    this.renderFileList();
}
// クリア
clearFile() {
    this.files = [];
    this.renderFileList();
}
// 吹き出しの画像プレビュー用に生成した objectURL をまとめて解放する。
// 新規チャット／履歴復元で吹き出しを破棄するタイミングで呼び、メモリを解放する。
revokeAttachmentPreviews() {
    if ( !Array.isArray( this._attachmentPreviewUrls ) ) {
        this._attachmentPreviewUrls = [];
        return;
    }
    for ( const url of this._attachmentPreviewUrls ) {
        try {
            URL.revokeObjectURL( url );
        } catch ( error ) {
            console.warn('プレビューURLの解放に失敗しました。', error );
        }
    }
    this._attachmentPreviewUrls = [];
}
// 選択中ファイルの表示リストを描画する
renderFileList() {
    const list = this.elements.fileList;
    if ( !list ) return;

    if ( !Array.isArray( this.files ) || !this.files.length ) {
        list.replaceChildren();
        return;
    }

    const items = this.files.map(( item, index ) => {
        const file = item.file;
        const li = document.createElement('li');
        li.classList.add('aiAssistantInputSelectFilesItem');
        if ( item.useLlm ) li.classList.add('aiAssistantInputSelectFilesItemUseLlm');

        // テキストファイルは編集、画像ファイルはプレビューのボタンを×ボタンの左に表示する
        const fileType = fn.fileTypeCheck( file.name );
        let openButton = '';
        if ( fileType === 'text') {
            openButton = fn.html.button( fn.html.icon('search'), 'itaButton aiAssistantInputSelectFilesOpen', { type: 'fileEdit', index: index, action: 'normal', title: '編集'});
        } else if ( fileType === 'image') {
            openButton = fn.html.button( fn.html.icon('search'), 'itaButton aiAssistantInputSelectFilesOpen', { type: 'filePreview', index: index, action: 'normal', title: 'プレビュー'});
        }

        li.innerHTML = `
            <span class="aiAssistantInputSelectFilesName">${fn.escape( file.name )}</span>
            <span class="aiAssistantInputSelectFilesSize">${this.formatFileSize( file.size )}</span>
            <label class="aiAssistantInputSelectFilesLlm" title="ONにするとファイルの中身をAIが読み取って解析します">
                <input type="checkbox" class="aiAssistantInputSelectFilesLlmCheck" data-type="fileToggle" data-index="${index}"${ item.useLlm ? ' checked': ''}>
                <span class="aiAssistantInputSelectFilesLlmSwitch" aria-hidden="true"></span>
                <span class="aiAssistantInputSelectFilesLlmText">AIで解析</span>
            </label>
            ${openButton}
            ${fn.html.button( fn.html.icon('cross'), 'itaButton aiAssistantInputSelectFilesRemove', { type: 'fileRemove', index: index, action: 'danger', title: '削除'})}`;
        return li;
    });
    list.replaceChildren( ...items );
}
// ファイルサイズを見やすい単位に整形する
formatFileSize( size ) {
    const byte = Number( size ) || 0;
    if ( byte < 1024 ) return `${byte} B`;
    const units = [ 'KB', 'MB', 'GB', 'TB'];
    let value = byte / 1024;
    let unitIndex = 0;
    while ( value >= 1024 && unitIndex < units.length - 1 ) {
        value /= 1024;
        unitIndex++;
    }
    return `${value.toFixed(1)} ${units[ unitIndex ]}`;
}
/*
##################################################
    ファイルの登録（LLMへ渡すメタ情報の作成）
##################################################
*/
// 添付ファイルをLLMへ渡せる形（メタ情報）に整える。
// ※ ITAのMCPサーバーにはファイルアップロード用のエンドポイントが無いため、ファイルの実体は
//    サーバーへ保存せず、画面側で file_id を採番してメタ情報だけを作る。ファイルの中身は
//    「AIで解析」がオンかつ対応形式の場合に、LLM層（AiAssistantLlm）が image / document の
//    contentブロックとして直接渡す。
async fileUploader( file ) {
    return {
        file_id: `local-${Date.now()}-${Math.random().toString( 36 ).slice( 2, 10 )}`,
        filename: file?.name ?? '',
        size: file?.size ?? '',
        mime_type: file?.type ?? ''
    };
}
// ファイルの実体をbase64（data URIなしの純粋なbase64）に変換する
fileToBase64( file ) {
    return new Promise(( resolve, reject ) => {
        const reader = new FileReader();
        reader.onload = () => {
            // "data:<mime>;base64,xxxx" の base64部分のみ取り出す
            const result = reader.result ?? '';
            const base64 = String( result ).split(',')[ 1 ] ?? '';
            resolve( base64 );
        };
        reader.onerror = () => reject( reader.error );
        reader.readAsDataURL( file );
    });
}
// ファイルの実体を生テキストに変換する
fileToText( file ) {
    return new Promise(( resolve, reject ) => {
        const reader = new FileReader();
        reader.onload = () => resolve( String( reader.result ?? '') );
        reader.onerror = () => reject( reader.error );
        reader.readAsText( file );
    });
}
// テキストファイルかどうかを判定する
isTextFile( file ) {
    const mimeType = file.type ?? '';
    if ( mimeType.startsWith('text/') ) return true;
    // text/ 以外でテキストとして扱うMIMEタイプ
    const textLikeTypes = [
        'application/json',
        'application/xml',
        'application/javascript',
        'application/x-yaml',
        'application/yaml'
    ];
    if ( textLikeTypes.includes( mimeType ) ) return true;
    // MIMEタイプが空の場合は拡張子で判定
    if ( mimeType === '') {
        const ext = ( file.name ?? '').split('.').pop().toLowerCase();
        const textExtensions = [
            'txt', 'md', 'csv', 'tsv', 'log', 'json', 'xml', 'yaml', 'yml',
            'js', 'ts', 'py', 'java', 'c', 'cpp', 'h', 'go', 'rb', 'php',
            'sh', 'sql', 'html', 'css', 'ini', 'conf', 'cfg', 'toml'
        ];
        return textExtensions.includes( ext );
    }
    return false;
}
// LLMがネイティブに中身を解析できる形式かどうかを判定する
// （AIサービス側の対応形式と一致させる：画像・PDF・テキスト）
isLlmSupportedFile( file ) {
    const mimeType = file.type ?? '';
    const supportedImageTypes = [ 'image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if ( supportedImageTypes.includes( mimeType ) ) return true;
    if ( mimeType === 'application/pdf') return true;
    if ( this.isTextFile( file ) ) return true;
    return false;
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   チャット HTML
//
////////////////////////////////////////////////////////////////////////////////////////////////////
// エラーをユーザ向けのわかりやすいメッセージに整形する
formatErrorMessage( error ) {
    const raw = error?.message ?? String( error ?? '');
    // fetch のネットワーク／接続エラー（"Failed to fetch" 等）はわかりやすい文言に置き換える
    if ( /failed to fetch|networkerror|network error|load failed/i.test( raw ) ) {
        return 'サーバーに接続できませんでした。ネットワーク接続を確認し、しばらくしてからもう一度お試しください。';
    }
    return raw;
}
// ユーザメッセージ
// rewindable : このメッセージを起点に会話を巻き戻せる（＝ユーザが実際に送信した
//   発言）場合に true。true のときだけ、吹き出し右上に操作メニュー（巻き戻し等）を出す。
//   選択肢への回答（tool_result）やシステム通知には出さない。
createUserMessageElement( text, attachments, rewindable = false ) {
    const el = document.createElement('li');
    el.classList.add('aiAssistantChatItem', 'aiAssistantChatUserMessage');
    el.innerHTML = `<div class="aiAssistantChatItemInner aiAssistantChatUserMessageInner"></div>`;

    // 巻き戻し等の操作メニュー（この時点まで会話を戻す）を吹き出しに付ける。
    if ( rewindable ) {
        el.classList.add('aiAssistantChatUserMessageRewindable');
        el.append( this.createMessageMenuElement() );
    }

    const p = document.createElement('p');
    p.innerText = text;
    el.querySelector('.aiAssistantChatItemInner').append( p );

    // 添付ファイルがあれば表示
    if ( Array.isArray( attachments ) && attachments.length ) {
        const inner = el.querySelector('.aiAssistantChatItemInner');
        const list = document.createElement('ul');
        list.classList.add('aiAssistantChatUserMessageFiles');
        attachments.forEach(( file ) => {
            const li = document.createElement('li');
            li.classList.add('aiAssistantChatUserMessageFile');
            // プレビューURLがあれば（ライブ表示中の画像）サムネイルを先頭に表示する。
            // クリックで添付時と同じプレビュー（fn.fileEditor）を開く。
            const previewHtml = file.previewUrl
                ? `<span class="aiAssistantChatUserMessageFilePreview" data-type="attachmentPreview" data-preview-url="${fn.escape( file.previewUrl )}" data-filename="${fn.escape( file.filename ?? '' )}" title="プレビュー">`
                    + `<img src="${fn.escape( file.previewUrl )}" alt="${fn.escape( file.filename ?? '' )}"></span>`
                : '';
            li.innerHTML = `
                ${previewHtml}
                <span class="aiAssistantChatUserMessageFileName">${fn.escape( file.filename ?? file.file_id ?? '' )}</span>
                <span class="aiAssistantChatUserMessageFileSize">${this.formatFileSize( file.size )}</span>`;
            if ( file.previewUrl ) li.classList.add('aiAssistantChatUserMessageFileHasPreview');
            list.appendChild( li );
        });
        inner.appendChild( list );
    }
    return el;
}
// ユーザメッセージの操作メニュー（吹き出し下側）を生成する。
// アイコンのみの操作ボタンを横並びで並べる（ホバー時に表示）。
// 現状は「この時点まで巻き戻す」のみ。将来的にフォーク等のボタンを追加できる作りにしておく。
createMessageMenuElement() {
    const menu = document.createElement('div');
    menu.classList.add('aiAssistantChatUserMessageMenu');
    // 操作ボタンの定義（今後ここに項目を追加する）。title はホバー時のツールチップ。
    const actions = [
        { type: 'rewindToHere', icon: 'return', title: 'この時点まで巻き戻す' },
    ];
    menu.innerHTML = actions.map(( action ) =>
        fn.html.button( fn.html.icon( action.icon ), 'itaButton aiAssistantChatUserMessageMenuButton popup', { type: action.type, action: 'default', title: action.title })
    ).join('');
    return menu;
}
// システムメッセージ（操作通知）
// ユーザの入力ではなく、システム操作（会話終了など）を区別して表示する。
createSystemMessageElement( text ) {
    const el = document.createElement('li');
    el.classList.add('aiAssistantChatItem', 'aiAssistantChatSystemMessage');
    el.innerHTML = `<div class="aiAssistantChatItemInner aiAssistantChatSystemMessageInner"></div>`;

    const p = document.createElement('p');
    p.innerText = text;
    el.querySelector('.aiAssistantChatItemInner').append( p );
    return el;
}
// 発言時刻を「年 / 月日 / 時刻」の3行スタックで表示する要素を作る。
// iso: ISO文字列（履歴の _timestamp など）。
// ・時刻が無い／不正な場合は null を返し、時刻を表示しない。
//   （タイムスタンプ未保存の古い履歴を復元したとき、現在時刻を誤表示しないため）
createTimestampElement( iso ) {
    if ( typeof iso !== 'string' || !iso ) return null;
    const d = new Date( iso );
    if ( isNaN( d.getTime() ) ) return null;
    const yyyy = d.getFullYear();
    const mm = String( d.getMonth() + 1 ).padStart( 2, '0');
    const dd = String( d.getDate() ).padStart( 2, '0');
    const hh = String( d.getHours() ).padStart( 2, '0');
    const mi = String( d.getMinutes() ).padStart( 2, '0');

    const span = document.createElement('span');
    span.classList.add('aiAssistantChatTime');
    // 機械可読な時刻も保持しておく（後からの再描画・デバッグ用）
    span.dataset.timestamp = d.toISOString();
    // 日付の比較キー。全てのタイムスタンプに持たせておき、次回の判定に使う。
    const dateKey = `${yyyy}-${mm}-${dd}`;
    span.dataset.date = dateKey;
    // 日付行は「最初の1件」と「日付が変わった直後の1件」だけ表示する。
    // 直前に描画済みのタイムスタンプ（＝chatList内で最後の .aiAssistantChatTime）と
    // 日付を比較し、同日なら日付行を省略する。DOMの現状を見るため、
    // 巻き戻しや履歴復元で並びが変わっても正しく判定できる。
    const prevTimeEls = this.elements.chatList?.querySelectorAll('.aiAssistantChatTime');
    const prevTimeEl = prevTimeEls?.length ? prevTimeEls[ prevTimeEls.length - 1 ] : null;
    const showDate = !prevTimeEl || prevTimeEl.dataset.date !== dateKey;
    span.innerHTML = ``
        + ( showDate ? `<span class="aiAssistantChatTimeDate">${mm}/${dd}</span>` : '' )
        + `<span class="aiAssistantChatTimeClock">${hh}:${mi}</span>`;
    return span;
}
// アシスタントメッセージ
createAssistantMessageElement( text, loading = false ) {
    const el = document.createElement('li');
    el.classList.add('aiAssistantChatItem', 'aiAssistantChatAssistantMessage');
    if ( loading ) el.classList.add('aiAssistantChatItemLoading');
    el.innerHTML = `<div class="aiAssistantChatAssistantMessageIcon"></div><div class="aiAssistantChatItemInner aiAssistantChatAssistantMessageInner">${ loading ? this.loadingHtml( text ): ''}</div>`;
    if ( text && loading === false ) {
        const inner = el.querySelector('.aiAssistantChatItemInner');
        inner.innerHTML = this.md.render( text );
        // tableをdiv.table-wrapperで囲む
        inner.querySelectorAll('table').forEach(( table ) => {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-wrapper');
            table.replaceWith( wrapper );
            wrapper.appendChild( table );
        });
        //
        inner.querySelectorAll('pre > code').forEach(( code ) => {
            if ( !code.classList.contains('hljs') ) {
                code.classList.add('codeBlock');
            }
        });
        // コードブロック（pre）の右上に「コピー」「入力欄にセット」ボタンを付与する
        inner.querySelectorAll('pre').forEach(( pre ) => {
            const wrapper = document.createElement('div');
            wrapper.classList.add('aiAssistantChatCodeBlock');
            pre.replaceWith( wrapper );
            wrapper.appendChild( this.createCodeToolbar() );
            wrapper.appendChild( pre );
        });
        // インラインコード（pre配下でないcode）にも同じボタンを付与する（ボタンは枠の外に浮かせる）
        inner.querySelectorAll(':not(pre) > code').forEach(( code ) => {
            const wrapper = document.createElement('span');
            wrapper.classList.add('aiAssistantChatInlineCode');
            code.replaceWith( wrapper );
            wrapper.appendChild( code );
            wrapper.appendChild( this.createCodeToolbar('aiAssistantChatCodeToolbarInline') );
        });
    }
    return el;
}
// コードのツールバー（コピー／入力欄にセット）要素を生成する
createCodeToolbar( extraClass ) {
    const toolbar = document.createElement('div');
    toolbar.classList.add('aiAssistantChatCodeToolbar');
    if ( extraClass ) toolbar.classList.add( extraClass );
    // クリップボードAPIはセキュアコンテキスト（HTTPS等）でのみ利用できるため、その場合だけコピーボタンを表示する
    const copyButton = ( window.isSecureContext && navigator.clipboard )
        ? fn.html.button( fn.html.icon('copy'), 'itaButton aiAssistantChatCodeButton popup', { type: 'codeCopy', action: 'default', title: 'クリップボードにコピー'})
        : '';
    toolbar.innerHTML =
        copyButton
        + fn.html.button( fn.html.icon('note'), 'itaButton aiAssistantChatCodeButton popup', { type: 'codeToInput', action: 'default', title: '入力欄にセット'});
    return toolbar;
}
// コード（ブロック／インライン）のテキストを取得する（ツールバーのボタンから呼び出す）
getCodeBlockText( button ) {
    const block = button.closest('.aiAssistantChatCodeBlock, .aiAssistantChatInlineCode');
    const target = block?.querySelector('pre code') ?? block?.querySelector('code') ?? block?.querySelector('pre');
    return target ? target.textContent : '';
}
// クリップボードへコピーする（コピーボタンはセキュアコンテキストでのみ表示される）
async copyToClipboard( text ) {
    try {
        await navigator.clipboard.writeText( text );
        return true;
    } catch ( error ) {
        console.error('クリップボードへのコピーに失敗しました。', error );
        return false;
    }
}
// ローディングHTML
loadingHtml( text ) {
    return `
    <div class="aiAssistantChatItemNowLoading">
        <div class="aiAssistantChatItemNowLoading-dot aiAssistantChatItemNowLoading-dot-1"></div>
        <div class="aiAssistantChatItemNowLoading-dot aiAssistantChatItemNowLoading-dot-2"></div>
        <div class="aiAssistantChatItemNowLoading-dot aiAssistantChatItemNowLoading-dot-3"></div>
        <div class="aiAssistantChatItemNowLoadingText">${fn.escape(text)}</div>
        <div class="aiAssistantChatItemNowLoading-dot aiAssistantChatItemNowLoading-dot-4"></div>
        <div class="aiAssistantChatItemNowLoading-dot aiAssistantChatItemNowLoading-dot-5"></div>
        <div class="aiAssistantChatItemNowLoading-dot aiAssistantChatItemNowLoading-dot-6"></div>
    </div>`;
}
// ユーザ選択肢
createUserChoiceElement( options ) {
    const el = document.createElement('li');
    el.classList.add('aiAssistantChatItem', 'aiAssistantChatUserChoice');
    el.innerHTML = `<div class="aiAssistantChatItemInner aiAssistantChatUserChoiceInner"></div>`;
    
    const list = document.createElement('ui');
    list.classList.add('aiAssistantChatUserChoiceList');
    // action（positive / negative / other）ごとにボタンの見た目とアイコンを切り替える。
    const choiceStyle = {
        positive: { action: 'positive', icon: 'check' },
        negative: { action: 'negative', icon: 'cross' },
        other:    { action: 'normal',   icon: 'circle' }
    };
    if ( Array.isArray(options) && options.length ) {
        for ( const option of options ) {
            // 旧形式（文字列）／新形式（{ label, action }）の両方を許容する。
            const normalized = this.normalizeChoiceOption( option );
            const style = choiceStyle[ normalized.action ] ?? choiceStyle.other;

            const item = document.createElement('li');
            item.classList.add('aiAssistantChatUserChoiceItem');

            const button = fn.html.iconButton( style.icon, fn.escape( normalized.label ), 'itaButton aiAssistantChatUserChoiceButton', { action: style.action, type: 'choice'});
            item.innerHTML = button;
            list.appendChild(item);
        }
    }

    const note = document.createElement('p');
    note.classList.add('aiAssistantChatUserChoiceNote');
    note.innerText = '回答をボタンで選択するか、下の入力欄に直接ご記入ください。';

    el.querySelector('.aiAssistantChatUserChoiceInner').append( list, note );
    return el;
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   チャット
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    チャットエリア初期化
##################################################
*/
initChatArea() {
    this.newChat = false;
    this.elements.chatBody.innerHTML = `<ul class="aiAssistantChatList"></ul>`;
    this.elements.chatList = this.elements.chatBody.querySelector('.aiAssistantChatList');
    this.elements.body.classList.remove('aiAssistantNewChat');
    this.elements.body.classList.add('aiAssistantChatNow');
    this.elements.body.querySelector('.aiAssistantDisclaimerMessage').style.display ='none';
    this.elements.settingButton.disabled = true;
    this.elements.closeChatButton.disabled = false;
}
/*
##################################################
    チャット更新
##################################################
*/
updateChat( message, scroll = true ) {
    // チャットエリア初期化
    if ( this.newChat === true && message.role === 'user') this.initChatArea();

    // 選択肢があれば削除
    const choiceItem = this.elements.chatList.querySelector('.aiAssistantChatUserChoice');
    if ( choiceItem ) choiceItem.remove();

    // 待機中があれば削除（何らかの理由で複数残ることがあるため、すべて消す）
    this.elements.chatList
        .querySelectorAll('.aiAssistantChatItemLoading')
        .forEach(( item ) => item.remove() );

    let el_messege;
    // markdown-it は文字列以外を渡すと例外を投げるため、必ず文字列へ変換する
    let messageText = message.text ?? '';
    if ( typeof messageText !== 'string') {
        messageText = messageText?.message ?? String( messageText );
    }

    switch ( message.role ) {
        // ユーザメッセージ
        case 'user':
            el_messege = this.createUserMessageElement( messageText, message.attachments, message.rewindable === true );
            break;
        // システムメッセージ（操作通知）
        case 'system':
            el_messege = this.createSystemMessageElement( messageText );
            break;
        // アシスタント待機中（再送などで文言を差し替える場合は message.text を渡す）
        case 'assistantWait':
            el_messege = this.createAssistantMessageElement( messageText || '思考中', true );
            break;
        // ツール実行中
        case 'toolRunning':
            el_messege = this.createAssistantMessageElement('ツール実行中', true );
            break;
        // アシスタントメッセージ
        case 'assistant':
            el_messege = this.createAssistantMessageElement( messageText );
            break;
        // ユーザ選択肢
        case 'userChoice':
            el_messege = this.createUserChoiceElement( message.options );
            break;

        default:
            console.warn('Unknown role type:', message.role );
    }

    if ( el_messege ) {
        // 巻き戻し起点となるユーザメッセージには、対応する履歴ブロックの位置を持たせる。
        // これを使って「この時点まで巻き戻す」で LLM 履歴を正確に切り詰める。
        // （ライブ送信時は historyIndex が未確定なので、送信側で後から stamp する）
        if ( message.role === 'user' && message.rewindable === true && Number.isInteger( message.historyIndex ) ) {
            el_messege.dataset.historyIndex = String( message.historyIndex );
        }
        // ひとつ前のメッセージもアシスタントの場合は連続クラスを付与
        if ( ['assistantWait', 'toolRunning', 'assistant'].includes( message.role )) {
            const prevItem = this.elements.chatList.lastElementChild;
            if ( prevItem?.classList.contains('aiAssistantChatAssistantMessage') ) {
                el_messege.classList.add('aiAssistantChatAssistantMessageChain');
            }
        }

        // 発言時刻を吹き出しの脇に表示する（ユーザ＝左隣、アシスタント＝右隣）。
        // ライブ時は message.timestamp（送信側で履歴にも保存した値）、
        // 復元時は履歴の _timestamp を渡す。待機中／ツール実行中の吹き出しには付けない。
        if ( ['user', 'assistant'].includes( message.role ) ) {
            const timeEl = this.createTimestampElement( message.timestamp );
            if ( timeEl ) {
                if ( message.role === 'user') {
                    // 右寄せの吹き出しの左隣に出すため、先頭に挿入する
                    el_messege.insertBefore( timeEl, el_messege.firstChild );
                } else {
                    // 左寄せの吹き出しの右隣に出すため、末尾に追加する
                    el_messege.appendChild( timeEl );
                }
            }
        }

        this.elements.chatList.append( el_messege );

        // スクロール
        if ( scroll ) {
            setTimeout( () => {
                this.scrollChatArea( el_messege );
            }, 100 );
        }
    }

    return el_messege;
}
/*
##################################################
    チャットスクロール
##################################################
*/
scrollChatArea( el_message, duration = 500 ) {
    const chatArea = this.elements.bodyInner;
    const startTop = chatArea.scrollTop;
    const targetTop = startTop
        + el_message.getBoundingClientRect().top
        - chatArea.getBoundingClientRect().top
        - 16;
    const distance = targetTop - startTop;

    // 進行中のスクロールアニメーションがあればキャンセル
    if ( this._scrollAnimationId ) cancelAnimationFrame( this._scrollAnimationId );

    const startTime = performance.now();
    // easeInOutQuad
    const easing = ( t ) => t < 0.5 ? 2 * t * t : 1 - Math.pow( -2 * t + 2, 2 ) / 2;

    const step = ( now ) => {
        const elapsed = now - startTime;
        const progress = duration > 0 ? Math.min( elapsed / duration, 1 ) : 1;
        chatArea.scrollTop = startTop + distance * easing( progress );
        if ( progress < 1 ) {
            this._scrollAnimationId = requestAnimationFrame( step );
        } else {
            this._scrollAnimationId = null;
        }
    };
    this._scrollAnimationId = requestAnimationFrame( step );
}
/*
##################################################
    メッセージ送信
##################################################
*/
async sendMessage( message, options = {} ) {
    // -----
    // ユーザメッセージ
    // -----
    // 先頭・末尾のスペースや改行を取り除く
    if ( typeof message === 'string') message = message.trim();
    if ( message === '') return;

    // 画面の吹き出しに表示する文言。指定があれば、LLMへ送る本文（message）とは
    // 別の短い文言を表示する（例：チャット終了時、長い指示文はLLMに送りつつ
    // 吹き出しは短い文言にする）。未指定なら本文をそのまま表示する。
    const displayText = ( typeof options.displayText === 'string' && options.displayText.trim() !== '')
        ? options.displayText
        : message;
    // システム操作（会話終了など）の場合は、ユーザ入力とは別のシステム通知として表示する。
    // LLMの履歴上は通常どおり user ターンだが、画面表示のみ role を分ける。
    const displayRole = ( options.systemAction === true ) ? 'system' : 'user';
    this.elements.body.classList.add('exchangingMessages');
    this.isRunning = true;

    // 通常のユーザメッセージ送信時は「チャット終了」ボタンを再活性化する。
    // （チャット終了操作の直後は無効化されているが、会話を続ける場合は再び閉じられるようにする）
    // システム操作（会話終了）自体の送信では再活性化しない。
    if ( options.systemAction !== true && this.elements.closeChatButton ) {
        this.elements.closeChatButton.disabled = false;
    }

    // 直前に選択肢（ask_user_choice）を出している場合、
    // ボタン選択・自由入力のどちらの回答も、その tool_use に対する tool_result として返す。
    // （tool_use の直後の user ターンは tool_result で始める必要があるため）
    const pendingChoiceToolId = this.pendingChoiceToolId;
    this.pendingChoiceToolId = null;
    // 分裂した余分な選択肢 tool_use の id（代表以外）。これらも tool_result を
    // 返さないと次回送信で未応答 tool_use となり API エラーになるため、まとめて返す。
    const pendingExtraChoiceToolIds = Array.isArray( this.pendingExtraChoiceToolIds ) ? this.pendingExtraChoiceToolIds : [];
    this.pendingExtraChoiceToolIds = [];
    // 選択肢と同じ応答に混在していた通常ツールの tool_result（退避分）。
    // 選択肢の tool_result と同じ user ターンでまとめて返す必要がある。
    const pendingToolResults = Array.isArray( this.pendingToolResults ) ? this.pendingToolResults : [];
    this.pendingToolResults = [];

    // Textareaの値を消す
    this.elements.message.value = '';

    // 発言時刻。画面表示（userMessage.timestamp）と履歴保存（send の options.timestamp）で
    // 同じ値を使い、ライブ表示と再開時表示がずれないようにする。
    const userTimestamp = new Date().toISOString();
    const userMessage = {
        role: displayRole,
        text: displayText,
        timestamp: userTimestamp,
        // 送信前の選択ファイルから表示用のメタ情報を作る
        attachments: ( Array.isArray( this.files ) ? this.files : [] ).map(( item ) => {
            const attachment = {
                filename: item.file.name,
                size: item.file.size,
            };
            // 画像はライブ表示用のプレビューURLを付与する。送信後は clearFile() で
            // ファイル実体が失われるため、実体がここにある間に objectURL を作っておく。
            // （履歴には画像実体を保存しないので、履歴復元時はプレビュー無しで表示される）
            if ( ( item.file.type ?? '').startsWith('image/') ) {
                attachment.previewUrl = URL.createObjectURL( item.file );
                // 新規チャット／復元時に revoke できるよう控えておく。
                if ( !Array.isArray( this._attachmentPreviewUrls ) ) this._attachmentPreviewUrls = [];
                this._attachmentPreviewUrls.push( attachment.previewUrl );
            }
            return attachment;
        }),
    };
    // システム操作（会話終了など）以外のユーザ発言は巻き戻しの起点にできる。
    // 選択肢への回答（tool_result になる）も含めて対象にする。
    // このとき吹き出しに操作メニュー（この時点まで巻き戻す）を表示する。
    // 対応する履歴上の位置（historyIndex）は送信直前に確定するため、後で stamp する。
    const isRewindableUserTurn = ( options.systemAction !== true );
    userMessage.rewindable = isRewindableUserTurn;
    // 中断・エラー時に「このターン全体」を視覚的に区別できるよう、ターン開始要素を保持する
    const turnStartEl = this.updateChat( userMessage );

    // LLMに送るペイロード。
    // 通常はテキスト（message）だが、選択肢への回答時は tool_result として返す。
    let sendPayload = message;
    // tool_result は「直前の assistant メッセージに対応する tool_use が存在する」ことが
    // 必須。停止・エラーでターンが巻き戻されたり履歴が復元・リセットされたりすると、
    // pendingChoiceToolId が指す tool_use が履歴に残っていない場合があり、その状態で
    // tool_result を送ると ValidationException（unexpected tool_use_id）になる。
    // そこで、実際に履歴末尾の assistant に存在する tool_use_id だけを tool_result 化し、
    // 対応が取れないものは破棄してテキスト送信にフォールバックする（自己修復）。
    if ( pendingChoiceToolId ) {
        const lastAssistantToolUseIds = this.getLastAssistantToolUseIds();
        const validChoiceId = lastAssistantToolUseIds.has( pendingChoiceToolId )
            ? pendingChoiceToolId : null;
        // 通常ツール結果（退避分）も、対応 tool_use が履歴に無いものは除外する。
        const validPendingToolResults = pendingToolResults.filter(
            ( r ) => r && lastAssistantToolUseIds.has( r.tool_use_id )
        );
        const validExtraIds = pendingExtraChoiceToolIds.filter(
            ( id ) => lastAssistantToolUseIds.has( id )
        );

        if ( validChoiceId ) {
            // 選択肢と同じ応答で先に実行済みの通常ツール結果（退避分）を先頭に置き、
            // 続けて選択肢への回答を tool_result として返す。
            // （tool_use の直後の user ターンは、その応答に含まれる全 tool_use 分の
            //   tool_result を含む必要があるため、まとめて1メッセージで送る）
            sendPayload = [
                ...validPendingToolResults,
                {
                    type: 'tool_result',
                    tool_use_id: validChoiceId,
                    content: message,
                },
                // 分裂した余分な選択肢 tool_use にも空応答を返し、未応答を防ぐ。
                ...validExtraIds.map(( id ) => ({
                    type: 'tool_result',
                    tool_use_id: id,
                    content: '（この選択肢はまとめて処理されました）',
                })),
            ];
        } else {
            // 対応する tool_use が履歴に見当たらない（巻き戻し・復元ズレ等）。
            // tool_result は送れないため、通常のテキストメッセージとして送る。
            console.warn('pendingChoiceToolId に対応する tool_use が履歴末尾に見つからないため、tool_result 送信を取りやめてテキスト送信にフォールバックします。', pendingChoiceToolId );
            sendPayload = message;
        }
    }

    // -----
    // ファイルアップロード（送信時に並列でアップロード）
    // -----
    let uploadedFiles = [];
    if ( Array.isArray( this.files ) && this.files.length ) {
        // ファイル処理中ダイアログ
        let process = fn.processingModal('添付ファイル処理中');

        // ファイルはすべてアップロードする
        const items = this.files.slice();
        try {
            const results = await Promise.all(
                items.map(( item ) => this.fileUploader( item.file ) )
            );
            // アップロード結果にLLM送信フラグを付与
            // useLlm : true ならファイルの実体（base64）も渡す
            uploadedFiles = await Promise.all( items.map( async ( item, i ) => {
                const mimeType = item.file.type ?? '';
                // supported : LLMがネイティブに中身を解析できる形式か（解析オフでも判定して渡す）
                const supported = this.isLlmSupportedFile( item.file );
                const entry = { ...results[ i ], useLlm: item.useLlm, mimeType, supported };
                // 解析オン かつ 対応形式のときだけファイルの実体を渡す
                if ( item.useLlm && supported ) {
                    if ( this.isTextFile( item.file ) ) {
                        // テキストファイルは生テキストで渡す
                        entry.text = await this.fileToText( item.file );
                    } else {
                        // それ以外はbase64で渡す
                        entry.data = await this.fileToBase64( item.file );
                    }
                }
                return entry;
            }));
        } catch ( error ) {
            console.error( error );
            alert('ファイルのアップロードに失敗しました。');
            this.isRunning = false;
            return;
        }
        // 送信したファイルはクリア
        this.clearFile();
        await this.sleep( 500 );

        // ダイアログを消す
        process.close();
    } else {
        await this.sleep( 500 );
    }

    // -----
    // アシスタントメッセージ（応答ループ）
    // -----
    // 応答ループは _runResponseLoop に切り出し、通常送信と「中断後の自動継続」で共用する。
    await this._runResponseLoop({
        sendPayload,
        uploadedFiles,
        turnStartEl,
        isRewindableUserTurn,
        // 最初のユーザターンにだけ渡す表示情報（displayText / systemAction / timestamp）
        firstSendOptions: { displayText: options.displayText, systemAction: options.systemAction, timestamp: userTimestamp },
        // 停止・エラー時に復元する、ターン開始前の保留状態
        savedPending: { pendingChoiceToolId, pendingExtraChoiceToolIds, pendingToolResults },
    });
}
/*
##################################################
    応答ループ
##################################################
*/
// LLMへの送信 → 応答（テキスト／ツール呼び出し）処理 → ツール実行 → 結果を返して再送、を
// 繰り返す中核ループ。通常のメッセージ送信（sendMessage）と、ページ離脱で中断された会話の
// 自動継続（_continueInterrupted）で共用する。
// ctx:
//   sendPayload         : 最初の送信ペイロード（テキスト / tool_result 配列 / 継続時は null）
//   uploadedFiles       : 最初のユーザターンで渡す添付（継続時は空）
//   turnStartEl         : このターンのユーザ発言要素（中断ターンの視覚区別用。継続時は null）
//   isRewindableUserTurn: 巻き戻し起点にできるユーザターンか
//   firstSendOptions    : 最初の送信に渡す表示情報（displayText / systemAction / timestamp）
//   savedPending        : 停止・エラー時に復元する保留状態（pendingChoiceToolId 等）
//   continuation        : true の場合、最初の送信は「継続」（新規 user を積まず alreadyPushed で送る）
async _runResponseLoop( ctx ) {
    let sendPayload = ctx.sendPayload;
    const { uploadedFiles, turnStartEl, isRewindableUserTurn, firstSendOptions, savedPending } = ctx;
    const savedPendingChoiceToolId = savedPending?.pendingChoiceToolId ?? null;
    const savedPendingExtraChoiceToolIds = Array.isArray( savedPending?.pendingExtraChoiceToolIds ) ? savedPending.pendingExtraChoiceToolIds : [];
    const savedPendingToolResults = Array.isArray( savedPending?.pendingToolResults ) ? savedPending.pendingToolResults : [];

    // LLM（AIサービスの会話）を用意する。新規チャット時に作成できていなかった場合
    // （通信エラーなど）も、送信のたびに作成を試みる。
    // 用意できない場合はターンを開始せず、エラーだけを表示して戻る。
    let llm = null;
    try {
        llm = await this.ensureLlm();
        if ( !llm ) throw new Error('ご利用の準備が完了していません。「AIアシスタント設定」から設定を完了してください。');
    } catch ( error ) {
        console.error( error );
        const errorMessage = this.formatErrorMessage( error );
        alert( errorMessage );
        this.updateChat({ role: 'assistant', text: errorMessage });
        this.isRunning = false;
        this.elements.body.classList.remove('exchangingMessages');
        return;
    }
    // フッターで切り替えたモデル（this.modelId）を、このターンの問い合わせから使う
    llm.setModel( this.modelId );

    // 実行中フラグ・表示・離脱再開マーカーをセット（自動継続の入口でも確実に立てる）
    this.isRunning = true;
    this.elements.body.classList.add('exchangingMessages');
    this._writeActiveChat( true );

    const maxAttempts = 100; // 最大試行回数
    let maxAttemptsFlag = true;
    let errorFlag = false;
    let stoppedFlag = false;
    // 長文脈でモデルがツール呼び出しを tool_use ではなくテキスト内の生の <invoke> として
    // 出力してしまうこと（フォーマット崩れ）への再送カウンタ。無限ループ防止のため上限を設ける。
    let invalidToolFormatRetries = 0;
    const maxInvalidToolFormatRetries = 5;
    // 再送時の待機表示に出す文言。処理が止まったように見せないため、
    // 次のループ先頭の待機スピナーへ「再試行中」である旨を伝える。null のときは通常の「思考中」。
    let waitMessage = null;
    // 停止時に巻き戻すためのLLM履歴チェックポイント（今回のターン開始前の件数）
    const historyCheckpoint = ( llm?.getChatHistory()?.length ) ?? 0;
    // 巻き戻し起点となるユーザ発言の吹き出しに、対応する履歴ブロックの位置を stamp する。
    // send() はこのターンの user メッセージを historyCheckpoint の位置に push するため、
    // その index を持たせておけば「この時点まで巻き戻す」で履歴を正確に切り詰められる。
    if ( isRewindableUserTurn && turnStartEl ) {
        turnStartEl.dataset.historyIndex = String( historyCheckpoint );
    }
    this._sendController = new AbortController();
    const { signal } = this._sendController;
    // 最初の送信を「継続」（新規 user を積まず、既存履歴末尾へ alreadyPushed で送る）にするか。
    // 中断後の自動継続や、ツール結果を先に履歴へ確定させた後の再送で true になる。
    let alreadyPushedNext = ( ctx.continuation === true );
    for ( let i = 0; i < maxAttempts; i++ ) {
        // アシスタント待機中表示（再送中は文言を差し替えて「再試行中」であることを伝える）
        this.updateChat({ role: 'assistantWait', text: waitMessage });
        waitMessage = null;

        // この回の送信を継続送信（再push抑止）にするか
        const alreadyPushed = alreadyPushedNext;
        alreadyPushedNext = false;

        // LLMにメッセージ送信（ファイルは初回のユーザメッセージ時のみ渡す）
        if ( signal.aborted ) {
            stoppedFlag = true;
            maxAttemptsFlag = false;
            break;
        }
        // 継続送信（alreadyPushed）時は、ペイロードは既に履歴へ積まれているのでファイル・表示情報は渡さない。
        const sendFiles = ( i === 0 && !alreadyPushed ) ? uploadedFiles : null;
        // 表示用の別文言（_displayText）や表示種別（_displaySystem）、発言時刻（timestamp）は、
        // 最初のユーザターンにだけ持たせる（再送・是正ターンのペイロードには付けない）。
        // timestamp は画面表示と履歴を一致させるため常に渡す（displayText/systemAction は
        // 送信側で有効値のみ採用されるので、そのまま渡して問題ない）。
        const sendOptions = ( i === 0 && !alreadyPushed ) ? firstSendOptions : undefined;
        let response;
        try {
            response = await llm.send( sendPayload, sendFiles, signal, { ...( sendOptions || {} ), alreadyPushed } );
        } catch ( error ) {
            // ユーザ都合の停止（AbortError）はエラー扱いしない
            if ( error?.name === 'AbortError' || signal.aborted ) {
                stoppedFlag = true;
                maxAttemptsFlag = false;
                break;
            }
            const errorMessage = this.formatErrorMessage( error );
            alert( errorMessage );
            errorFlag = true;
            maxAttemptsFlag = false;
            this.updateChat({
                role: 'assistant',
                text: errorMessage
            });
            break;
        }

        // 会話ID（履歴の保存先）は最初の送信で確定するため、中断再開マーカーへ書き戻す。
        // これで、ツールを使わない応答の途中でページを閉じても、この会話IDから自動再開できる。
        this._writeActiveChat( true );

        if ( response.stop_reason === 'max_tokens') {
            console.warn('LLMからの応答が最大トークン数に達しました。ループを終了します。');
            alert('LLMからの応答が最大トークン数に達しました。');
            maxAttemptsFlag = false;
            errorFlag = true;
            break;
        }

        // 長文脈になるとモデルが本来 tool_use（構造化ツール呼び出し）で出すべきものを、
        // text ブロック内に生の <invoke name="..."> として書いてしまうことがある（フォーマット崩れ）。
        // このまま表示するとユーザに <invoke> タグが露出し、ツールも実行されない。
        // 検知したら、その応答は表示・実行せずに履歴からこのターンの assistant を巻き戻し、
        // 是正指示を添えて同じ入力で再送する（＝再処理）。
        const hasRawInvokeInText = ( response.content ?? [] ).some(
            ( block ) => block.type === 'text' && /<(?:antml:)?invoke\b/i.test( block.text ?? '' )
        );
        if ( hasRawInvokeInText ) {
            // モデルが吐いた壊れた assistant ターンを履歴から除去（次回送信の整合性維持）。
            if ( llm && typeof llm.getChatHistory === 'function' ) {
                const messages = llm.getChatHistory();
                if ( Array.isArray( messages ) && messages.length && messages[ messages.length - 1 ].role === 'assistant') {
                    messages.pop();
                    if ( typeof llm.setChatHistory === 'function' ) llm.setChatHistory( messages );
                }
            }
            if ( invalidToolFormatRetries < maxInvalidToolFormatRetries ) {
                invalidToolFormatRetries++;
                console.warn(`ツール呼び出しがテキスト内の <invoke> として出力されました。tool_use での再出力を促して再送します（${invalidToolFormatRetries}/${maxInvalidToolFormatRetries}）。`);
                // 処理が止まったように見えないよう、次の待機表示で再試行中である旨を画面に出す。
                waitMessage = `応答を調整しています…（再試行 ${invalidToolFormatRetries}/${maxInvalidToolFormatRetries}）`;
                // 是正指示を user メッセージとして返し、tool_use 機能での呼び出し直しを促す。
                sendPayload = '直前の応答でツール呼び出しを <invoke> というテキストとして出力しましたが、これは誤りです。'
                    + 'テキストとして <invoke> を書かず、必ず tool_use 機能を使ってツールを呼び出し直してください。';
                continue;
            }
            // 再送上限に達した：ユーザに状況を伝えてループを終了する（壊れたタグは表示しない）。
            console.error('ツール呼び出しのテキスト出力が規定回を超えて解消しませんでした。');
            this.updateChat({
                role: 'assistant',
                text: '申し訳ありません。処理が正しく行えませんでした。お手数ですが、直前の指示をもう一度お送りください。'
            });
            errorFlag = true;
            maxAttemptsFlag = false;
            break;
        }

        // 応答に含まれる選択肢（ask_user_choice）の tool_use を、内容を処理する前に先に検査する。
        // options が文字列化していたり、label/action が options の外に漏れていたり、
        // 1応答に複数の選択肢 tool_use が分裂して出ている等のフォーマット崩れを検知したら、
        // その応答は表示・処理せずに履歴からこのターンの assistant を巻き戻し、
        // 正しい形式での呼び出し直しを促して再送する（＝ <invoke> テキスト崩れと同じ扱い）。
        const choiceToolBlocks = ( response.content ?? [] ).filter(
            ( block ) => block.type === 'tool_use' && this.isUiChoiceTool( block.name )
        );
        if ( choiceToolBlocks.length && this.isChoiceResponseMalformed( choiceToolBlocks ) ) {
            if ( invalidToolFormatRetries < maxInvalidToolFormatRetries ) {
                // モデルが吐いた壊れた assistant ターンを履歴から除去（次回送信の整合性維持）。
                if ( llm && typeof llm.getChatHistory === 'function' ) {
                    const messages = llm.getChatHistory();
                    if ( Array.isArray( messages ) && messages.length && messages[ messages.length - 1 ].role === 'assistant') {
                        messages.pop();
                        if ( typeof llm.setChatHistory === 'function' ) llm.setChatHistory( messages );
                    }
                }
                invalidToolFormatRetries++;
                console.warn(`ask_user_choice のパラメータ形式が崩れていました。正しい形式での再出力を促して再送します（${invalidToolFormatRetries}/${maxInvalidToolFormatRetries}）。`);
                // 処理が止まったように見えないよう、次の待機表示で再試行中である旨を画面に出す。
                waitMessage = `応答を調整しています…（再試行 ${invalidToolFormatRetries}/${maxInvalidToolFormatRetries}）`;
                // 是正指示を user メッセージとして返し、正しい形式での呼び出し直しを促す。
                sendPayload = '直前の ask_user_choice の呼び出しはパラメータ形式が誤っていました。'
                    + '選択肢はすべて options という1つの配列にまとめ、各要素を {"label": "表示文言", "action": "positive|negative|other"} という形式のオブジェクトにしてください。'
                    + 'label や action を options の外側に置いたり、options を文字列にしたり、選択肢ごとに ask_user_choice を分けて呼んだりしてはいけません。'
                    + 'ask_user_choice を1回だけ、正しい形式で呼び出し直してください。';
                continue;
            }
            // 再送上限に達した：可能な範囲で救済（mergeChoiceBlocks）して表示し、行き止まりを避ける。
            console.warn('ask_user_choice のフォーマット崩れが規定回を超えて解消しませんでした。可能な範囲で救済して表示します。');
        }

        // 中断耐性：この応答が tool_use を含む場合、ツール実行に入る前にサーバへ保存する。
        // 実行に時間のかかるツール（ドライバー実行など）の最中にページを閉じても「呼び出したこと」が
        // 履歴に残るため、再開時に同じ操作を再実行せず状況を確認できる（未応答 tool_use は再開時に
        // プレースホルダで整合を取る）。テキストのみの応答はツール結果保存／完了時保存でカバーされるため省く。
        // 保存はキュー化・版管理された非同期処理のため、ここでは待たずに投げる（会話速度に影響しない）。
        const responseHasToolUse = ( response.content ?? [] ).some(( block ) => block.type === 'tool_use' );
        if ( responseHasToolUse ) this._enqueueHistorySafe();

        const toolsResult = [];
        // 選択肢（ask_user_choice）の tool_use は、まとめて後段で処理する。
        // フォーマット崩れで1応答に複数の選択肢 tool_use が出ることがあるため、
        // ここで一旦集めておき、1つの選択肢UIへ統合する（下の mergeChoiceBlocks）。
        const choiceBlocks = [];
        for ( const block of response.content ?? [] ) {
            switch ( block.type ) {
                case 'text':
                    this.updateChat({
                        role: 'assistant',
                        text: block.text,
                        // 送信側（send）が履歴に付けた応答時刻と同じ値を表示に使う
                        timestamp: response._timestamp
                    });
                    break;

                case 'tool_use':
                    if ( !this.uiTools.includes( block.name ) ) {
                        const toolRunningEl = this.updateChat({ role: 'toolRunning'});
                        try {
                            // signal を渡し、停止時は MCP fetch / 進捗ポーリングごと中断する
                            const toolResult = await this.executeTool( block, toolRunningEl, signal );
                            toolsResult.push( toolResult );
                        } catch ( error ) {
                            // ユーザ都合の停止（AbortError）はエラー扱いせず、ターンを巻き戻す
                            if ( error?.name === 'AbortError' || signal.aborted ) {
                                stoppedFlag = true;
                            } else {
                                const errorMessage = this.formatErrorMessage( error );
                                alert( errorMessage );
                                errorFlag = true;
                                this.updateChat({ role: 'assistant', text: errorMessage });
                            }
                            maxAttemptsFlag = false;
                        }
                    } else if ( this.isUiChoiceTool( block.name ) ) {
                        // ユーザ選択肢は集約して後でまとめて処理する
                        choiceBlocks.push( block );
                    } else {
                        // 即時実行の画面専用ツール（display_html 等）。
                        // 画面に表示し、LLMには結果（表示した旨）だけを tool_result で返す。
                        const uiToolResult = this.uiTool( block.name )?.execute( block );
                        if ( uiToolResult ) toolsResult.push( uiToolResult );
                    }
                    break;

                case 'thinking':
                    // 何もしない
                    break;

                default:
                    console.warn('Unknown content type:', block.type );
                    break;
            }
            // 停止・エラーが発生したら残りのブロック処理を打ち切る
            if ( stoppedFlag || errorFlag ) break;
        }

        // 停止・エラー時はループを抜けて後段の巻き戻し処理へ
        if ( stoppedFlag || errorFlag ) break;

        // 集約した選択肢 tool_use を1つの選択肢UIに統合して表示する。
        // （分裂した複数 tool_use を1つにまとめ、代表以外の tool_use_id は
        //   未応答にならないよう pendingExtraChoiceToolIds へ退避する）
        if ( choiceBlocks.length ) {
            this.askUserChoice( this.mergeChoiceBlocks( choiceBlocks ) );
        }

        // 応答に選択肢（ask_user_choice）が含まれていた場合は、ユーザーの回答を待つ。
        // このとき、同じ応答に通常ツールも混在していた（＝ toolsResult がある）ら、
        // その tool_result を自動継続で送ってしまうと、選択肢の tool_use が
        // tool_result 未応答のまま送信され API エラー（ValidationException）になる。
        // そこで通常ツールの結果はバッファに退避し、ユーザーが選択肢に回答したときに
        // 選択肢の tool_result とまとめて返す。
        if ( this.pendingChoiceToolId ) {
            this.pendingToolResults = toolsResult;
            // 選択待ちで一旦ユーザに制御が戻るため、ここまでに更新されたページのリンクを表示する。
            this.renderUpdatedMenuLinks();
            maxAttemptsFlag = false;
            break;
        }

        // ツール結果があればLLMに返す
        if ( toolsResult.length ) {
            // 中断耐性（案1）：ツール結果を送信を待たずに履歴へ確定させる。
            // これにより、この後のLLM呼び出し中にページを閉じても「実行済みの操作とその結果」が失われず、
            // 再開時は整合した履歴（tool_use と tool_result が対）から続きを継続できる。
            // （tool_result は message で送れないため、続く継続送信が履歴を全置換して保存する）
            llm.appendToolResults( toolsResult );
            // 次回送信は継続送信（履歴末尾の tool_result をそのままLLMへ）。ペイロードの再pushはしない。
            sendPayload = null;
            alreadyPushedNext = true;
        } else {
            maxAttemptsFlag = false;
            break;
        }
    }

    if ( stoppedFlag || errorFlag ) {
        // ユーザ都合の停止、またはLLM／ツール実行のエラー：
        //   ・待機中／ツール実行中インジケータを消す
        //   ・LLM履歴を今回のターン開始前まで巻き戻す
        //     （ユーザメッセージ／tool_result 未応答の tool_use が残ると次回送信で API エラーになるため。
        //       500エラー時は send() 側で tool_result 入り user のみ pop され、未応答 tool_use を持つ
        //       assistant が履歴末尾に残るため、ここでターンごと巻き戻して整合性を保つ）
        //   ・履歴保存はしない
        this.elements.chatList
            ?.querySelectorAll('.aiAssistantChatItemLoading')
            .forEach(( item ) => item.remove() );

        if ( llm && typeof llm.getChatHistory === 'function' ) {
            const messages = llm.getChatHistory();
            if ( Array.isArray( messages ) && messages.length > historyCheckpoint ) {
                messages.length = historyCheckpoint;
                if ( typeof llm.setChatHistory === 'function' ) llm.setChatHistory( messages );
            }
        }

        // 選択肢への回答中に停止・エラーが起きた場合、直前の tool_use が tool_result 未応答のまま残る。
        // 次回送信で tool_result として返せるよう pendingChoiceToolId を復元する。
        // 同じ応答に混在していた通常ツールの結果（退避分）も、次回送信で選択肢の
        // tool_result とまとめて返せるよう合わせて復元する（片方だけ残すと未応答 tool_use になる）。
        if ( savedPendingChoiceToolId ) {
            this.pendingChoiceToolId = savedPendingChoiceToolId;
            this.pendingToolResults = savedPendingToolResults;
            this.pendingExtraChoiceToolIds = savedPendingExtraChoiceToolIds;
        }

        // このターンで表示された吹き出し（ユーザ発言～以降のAI/ツール）はすべて履歴から
        // 巻き戻されており「生きていない」ため、専用クラスで視覚的に区別する。
        this.markTurnAborted( turnStartEl );

        // 送信済みユーザメッセージのバブルに停止ラベルを付与
        this.markLastUserMessageStopped();

        // ターンを巻き戻したため、控えていた更新メニューのリンクは表示しない。
        // （ITA側の更新自体は取り消せないが、中断ターンの吹き出しとして出すのは紛らわしいため）
        this._turnUpdatedMenus = new Map();
    } else if ( maxAttemptsFlag ) {
        alert('LLMからの応答が規定回を超えました。ループを終了します。');
        console.log('LLMからの応答が規定回を超えました。ループを終了します。');
    } else {
        // 応答が正常に完了した。更新された ITA ページへのリンクをまとめて表示する。
        this.renderUpdatedMenuLinks();
        // 履歴登録（非同期）。保存失敗が未処理の Promise 拒否にならないよう安全ラッパーで投げる。
        if ( !errorFlag ) {
            this._enqueueHistorySafe();
        }
    }

    // 応答完了
    this.isRunning = false;
    this.elements.body.classList.remove('exchangingMessages');
    // 実行が終わったので離脱再開マーカーを「実行中でない」に更新する。
    // （正常完了・停止・エラーいずれもここを通るため、次回読込で誤って自動再開しない）
    this._writeActiveChat( false );
    return;
}
// 停止メソッド
stopMessage() {
    this._sendController?.abort();
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Movement
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    ドライバー実行進捗
##################################################
*/
// execute-driver / dryrun-driver の結果から execution_no を取り出し、
// 進捗を購読して実行状況をバブルに反映する。完了状態まで待ってから、
// 確定した最終結果（{type, status, result} など）を返す。対象外や取得失敗時は null。
async watchDriverProgress( toolUse, toolResult, runningEl ) {
    const DRIVER_TOOLS = ['execute-driver', 'dryrun-driver'];
    if ( !DRIVER_TOOLS.includes( toolUse.name ) ) return null;

    // ローディングclassをremove
    runningEl.classList.remove('aiAssistantChatItemLoading');

    // execution_no を取り出す（result.data.execution_no を想定。ゆらぎに対応）
    const structured = toolResult?.result?.structuredContent ?? {};
    if ( structured.isError === true || toolResult?.result?.isError === true ) return null;
    const apiResult = structured.result ?? {};
    const data = apiResult.data ?? apiResult;
    const executionNo = data?.execution_no ?? '';
    if ( !executionNo ) {
        console.warn('watchDriverProgress: execution_no が取得できませんでした', toolResult );
        return null;
    }

    // 実行メニュー（execution_*）→ ステータス確認メニュー（check_operation_status_*）へ変換
    console.log('toolUse: ', toolUse );
    const execMenu = toolUse.arguments?.menu ?? toolUse.input?.menu ?? '';
    const statusMenu = execMenu.startsWith('execution_')
        ? execMenu.replace(/^execution_/, 'check_operation_status_')
        : execMenu;
    if ( !statusMenu ) {
        console.warn('watchDriverProgress: ステータス確認メニューを導出できませんでした', execMenu );
        return null;
    }
    const movementName = toolUse.arguments?.movement_name ?? '';
    const operationName = toolUse.arguments?.operation_name ?? '';
    const execListMenu = this.drivers?.[ statusMenu ]?.executionListMenu ?? '';

    // Movement HTML
    const movement = this.movementElement( statusMenu, execListMenu, movementName, operationName, executionNo );
    runningEl.querySelector('.aiAssistantChatAssistantMessageInner').replaceChildren( movement );

    try {
        return await this.pollDriverStatus( statusMenu, executionNo, runningEl );
    } catch ( error ) {
        console.warn('watchDriverProgress: 進捗監視でエラー', error );
        return null;
    }
}
// ドライバー実行の終了ステータス（driver-control.md 準拠）
static DRIVER_FINAL_STATES = [
    'Completed',
    'Completed (error)',
    'Unexpected error',
    'Emergency stop',
    'Unexecuted (schedule)',
    'Schedule canceled'
];
// 進捗ポーリング設定
static PROGRESS_POLL_INTERVAL = 5000; // ミリ秒
static PROGRESS_MAX_DURATION = 3600000; // ミリ秒（保険の上限）
// get-driver-status を一定間隔でポーリングして実行状況をバブルに反映する。
// クライアント側で毎回 CommonAuth.getToken() の最新トークンを使って直接叩く。
// 終了状態に達したら { type:'done', status, result } を返す。
pollDriverStatus( menu, executionNo, runningEl ) {
    return new Promise(async ( resolve ) => {
        const { signal } = this._sendController ?? {};
        const interval = AiAssistantChat.PROGRESS_POLL_INTERVAL;
        const maxDuration = AiAssistantChat.PROGRESS_MAX_DURATION;
        let lastStatus = null;
        let elapsed = 0;

        while ( elapsed <= maxDuration ) {
            if ( signal?.aborted ) {
                resolve({ type: 'error', message: '進捗監視を中断しました' });
                return;
            }

            let statusResult;
            try {
                const response = await AiAssistantChat.fetchWithRetry( AiAssistantChat.apiUrl.mcp(), {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        // 毎回最新トークンを取得する（長時間監視での401対策）
                        "Authorization": `Bearer ${this.getToken()}`
                    },
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        id: 1,
                        method: "tools/call",
                        params: {
                            name: 'get-driver-status',
                            arguments: { menu, execution_no: executionNo }
                        }
                    }),
                    signal
                });
                statusResult = await response.json();
            } catch ( error ) {
                if ( error?.name === 'AbortError') {
                    resolve({ type: 'error', message: '進捗監視を中断しました' });
                    return;
                }
                console.warn('pollDriverStatus: ステータス取得でエラー', error );
                resolve({ type: 'error', message: fn.jsonStringify( error ) });
                return;
            }

            // ツール自体がエラーを返した場合は監視を打ち切る
            const structured = statusResult?.result?.structuredContent ?? {};
            if ( structured.isError === true || statusResult?.result?.isError === true ) {
                const message = this._extractToolErrorText( statusResult );
                console.warn('pollDriverStatus: get-driver-status がエラー応答', message );
                resolve({ type: 'error', message });
                return;
            }

            // status を含むノードを取得し、そこから status と同階層の result_data も拾う
            const statusNode = this._findDriverStatusNode( structured );
            const status = this._statusFromNode( statusNode );
            const resultDataName = statusNode?.result_data ? `ResultData_${executionNo}.zip`: null;

            // 変化があったときだけ表示更新（初回は必ず反映）
            if ( status && status !== lastStatus ) {
                lastStatus = status;
                this.updateToolProgress( runningEl, status, false, resultDataName );
            }

            // 終了状態なら done を返して終了
            if ( AiAssistantChat.DRIVER_FINAL_STATES.includes( status )) {
                this.updateToolProgress( runningEl, status, true, resultDataName );
                resolve({ type: 'done', status, result: structured.result ?? null });
                return;
            }

            // 停止時は sleep を待たず即座に中断できるよう、signal で待機を打ち切る
            await this.sleepOrAbort( interval, signal );
            elapsed += interval;
        }

        // 上限に達した場合
        this.updateToolProgress( runningEl, '進捗確認がタイムアウトしました', true );
        resolve({ type: 'timeout', message: 'Progress polling exceeded max duration' });
    });
}
// signal が abort されたら待機を即座に打ち切る sleep（進捗ポーリングの応答性向上用）
sleepOrAbort( time, signal ) {
    return new Promise(( resolve ) => {
        if ( signal?.aborted ) { resolve(); return; }
        const timer = setTimeout(() => {
            signal?.removeEventListener?.('abort', onAbort );
            resolve();
        }, time );
        const onAbort = () => {
            clearTimeout( timer );
            resolve();
        };
        signal?.addEventListener?.('abort', onAbort, { once: true });
    });
}
// get-driver-status で探索する status 系キー（優先順）
static STATUS_KEYS = ['status', 'execution_status', 'operation_status'];
// get-driver-status の structuredContent から status を含むノード（オブジェクト）を探す。
// data.execution_list.parameter.status などネストが深いため再帰探索する（構造のゆらぎに対応）。
// status と同階層の result_data 等も併せて取得したい場合はこのノードから拾う。
_findDriverStatusNode( structured ) {
    const result = structured?.result;
    if ( !result || typeof result !== 'object') return null;

    const search = ( node ) => {
        if ( Array.isArray( node )) {
            for ( const item of node ) {
                const found = search( item );
                if ( found ) return found;
            }
            return null;
        }
        if ( node && typeof node === 'object') {
            // status系キーを持つノードを優先
            for ( const key of AiAssistantChat.STATUS_KEYS ) {
                if ( typeof node[ key ] === 'string' && node[ key ]) return node;
            }
            for ( const val of Object.values( node )) {
                const found = search( val );
                if ( found ) return found;
            }
        }
        return null;
    };
    return search( result );
}
// ノードから status 系キーの値を取り出す。
_statusFromNode( node ) {
    if ( !node || typeof node !== 'object') return '';
    for ( const key of AiAssistantChat.STATUS_KEYS ) {
        if ( typeof node[ key ] === 'string' && node[ key ]) return node[ key ];
    }
    return '';
}
// get-driver-status の structuredContent から status 文字列を取り出す。
_extractDriverStatus( structured ) {
    return this._statusFromNode( this._findDriverStatusNode( structured ));
}
// tool_result のエラーテキストを取り出す（表示・ログ用）
_extractToolErrorText( statusResult ) {
    const content = statusResult?.result?.content;
    if ( Array.isArray( content )) {
        const text = content.find(( c ) => c.type === 'text')?.text;
        if ( text ) return text;
    }
    const structured = statusResult?.result?.structuredContent ?? {};
    return structured.error ?? statusResult?.error?.message ?? '進捗確認に失敗しました';
}
// 進捗バブルの表示を更新する
updateToolProgress( runningEl, statusText, done, resultDataName ) {
    if ( !runningEl ) return;

    const movementAreaEl = runningEl.querySelector('.movementArea');
    const nodeEl = runningEl.querySelector('.node');
    const emergencyStopButton = runningEl.querySelector('.movementEmergencyStopButton');
    const statusCheckButton = runningEl.querySelector('.movementStatusCheckButton');
    const resultDownloadButton = runningEl.querySelector('.movementResultDownloadButton');
    if ( nodeEl ) {
        statusCheckButton.disabled = false;
        switch ( statusText ) {
            // 準備中
            case 'Preparing':
                movementAreaEl.setAttribute('data-result', 'ready');
                nodeEl.classList.add('ready'); break;
            // 実行中
            case 'Executing':
                movementAreaEl.setAttribute('data-result', 'running');
                emergencyStopButton.disabled = false;
                nodeEl.classList.add('running'); break;
            // 完了
            case 'Completed':
                emergencyStopButton.disabled = true;
                movementAreaEl.setAttribute('data-result', 'done');
                nodeEl.querySelector('.node-result').setAttribute('data-result-text', 'DONE');
                nodeEl.classList.add('complete'); break;
            // エラー
            case 'Completed (error)':
            case 'Unexpected error':
                emergencyStopButton.disabled = true;
                movementAreaEl.setAttribute('data-result', 'error');
                nodeEl.querySelector('.node-result').setAttribute('data-result-text', 'ERROR');
                nodeEl.classList.add('complete'); break;
            // 緊急停止
            case 'Emergency stop':
                emergencyStopButton.disabled = true;
                movementAreaEl.setAttribute('data-result', 'stop');
                nodeEl.querySelector('.node-result').setAttribute('data-result-text', 'STOP');
                nodeEl.classList.add('complete'); break;
            default:
        }

        // 結果データ
        if ( resultDataName ) {
            resultDownloadButton.setAttribute('data-filename', resultDataName );
            resultDownloadButton.disabled = false;
        } else {
            resultDownloadButton.setAttribute('data-filename', '');
            resultDownloadButton.disabled = true;
        }
    }
}
// Movement HTML
movementElement( statusMenu, execListMenu, movementName, operationName, executionNo ) {
    const menu = {
        Main: [
            { html: {
                    // 作業状態確認
                    html: fn.html.iconButton(
                        'note',
                        '作業状態確認',
                        'itaButton operationMenuButton movementStatusCheckButton',
                        {
                            type: 'movementStatusCheck',
                            action: 'default',
                            disabled: true,
                            'execution-no': executionNo,
                            'status-menu': statusMenu
                        }
                    )
                }
            },
            { html: {
                    // 結果データ
                    html: fn.html.iconButton(
                        'download',
                        '結果データ',
                        'itaButton operationMenuButton movementResultDownloadButton',
                        {
                            type: 'movementResultDownload',
                            action: 'default',
                            disabled: true,
                            'execution-no': executionNo,
                            'exec-list-menu': execListMenu
                        }
                    )
                }
            }
        ],
        Sub: [
            { html: {
                    // 緊急停止
                    html: fn.html.iconButton(
                        'stop',
                        getMessage.FTE05004,
                        'itaButton operationMenuButton movementEmergencyStopButton',
                        {
                            type: 'movementEmergencyStop',
                            action: 'danger',
                            disabled: true,
                            'execution-no': executionNo,
                            'status-menu': statusMenu
                        }
                    )
                }
            }
        ]
    };
    const movement = document.createElement('div');
    movement.innerHTML = `
    ${fn.html.operationMenu( menu )}
    <div class="movementArea" data-result="">
        <div class="movementAreaInner">
            <div class="node ${this.drivers[statusMenu]?.movementClassName} operation">
                <div class="node-main">
                    <div class="node-terminal node-in connected">
                        <span class="connect-mark"></span>
                        <span class="hole">
                            <span class="hole-inner"></span>
                        </span>
                    </div>
                    <div class="node-body">
                        <div class="node-circle">
                            <span class="node-gem">
                                <span class="node-gem-inner">${this.drivers[statusMenu]?.movementGem}</span>
                            </span>
                            <span class="node-running"></span>
                            <span class="node-result node-jump popup darkPopup" title="作業状態確認"></span>
                        </div>
                        <div class="node-type">
                            <span>${this.drivers[statusMenu]?.movementType}</span>
                        </div>
                        <div class="node-name">
                            <span class="operationStatusData" data-type="movement_name">${fn.escape( movementName )}</span>
                        </div>
                    </div>
                    <div class="node-terminal node-out connected">
                        <span class="connect-mark"></span>
                        <span class="hole">
                            <span class="hole-inner"></span>
                        </span>
                    </div>
                </div>
                <div class="node-operation">
                    <dl class="node-operation-body">
                        <dt class="node-operation-name">OP</dt>
                        <dd class="node-operation-data">${fn.escape( operationName )}</dd>
                    </dl>
                    <div class="node-operation-border"></div>
                </div>
            </div>
        </div>
        <div class="movementWaiting">${this.loadingHtml('待機中')}</div>
    </div>`;
    const driverEl = movement.querySelector('.node-result');
    driverEl.setAttribute('data-execution-no', executionNo );
    driverEl.setAttribute('data-status-menu', statusMenu );

    return movement;
}
// Movement緊急停止
async movementStop( button ) {
    const driver = button.dataset.statusMenu;
    const executionNo = button.dataset.executionNo;
    if ( !driver || !executionNo ) {
        alert('Driverまたは実行No.が不明です。');
        return;
    }
    button.disabled = true;
    const url = `/menu/${driver}/driver/${executionNo}/scram/`;
    if ( window.confirm(getMessage.FTE02044) ) {
        try {
            const result = await fn.fetch( url, null, 'PATCH', {});
            alert( result );
        } catch ( error ) {
            alert( error.message ?? '緊急停止に失敗しました。');
            button.disabled = false;
        }
    } else {
        button.disabled = false;
    }
    return;
}
// 作業状態確認
async movementExecuteCheck( resultEl ) {
    const menu = resultEl.dataset.statusMenu;
    const executionNo = resultEl.dataset.executionNo;
    if ( menu && executionNo ) {
        resultEl.disabled = true;
        await fn.modalIframe( menu + '&execution_no=' + executionNo, getMessage.FTE02128, { width: '960px'} );
        resultEl.disabled = false;
    }
    return;
}
// 結果データダウンロード
async movementResultDownload( button ) {
    const menu = button.dataset.execListMenu;
    const executionNo = button.dataset.executionNo;
    const filename = button.dataset.filename;
    if ( menu && executionNo && filename ) {
        button.disabled = true;
        const endPoint = `/menu/${menu}/${executionNo}/result_data/file/`;
        try {
            const file = await fn.getFile( endPoint, 'GET', null, { title: getMessage.FTE00185 })
            await fn.download('file', file, filename );
        } catch ( error ) {
            if ( error !== 'break') {
                console.error( error );
                alert( getMessage.FTE00179 );
            }
        }
        button.disabled = false;
    }
    return;
}
drivers = {
    check_operation_status_ansible_role: {
        movementType: 'Ansible Legacy Role',
        movementGem: 'ALR',
        movementClassName: 'node-ansible-legacy-role',
        movementListMenu: 'movement_list_ansible_role',
        targetHostMenu: 'target_host_ansible_role',
        substValueMenu: 'subst_value_list_ansible_role',
        executionListMenu: 'execution_list_ansible_role'
    },
    check_operation_status_ansible_legacy: {
        movementType: 'Ansible Legacy',
        movementGem: 'AL',
        movementClassName: 'node-ansible-legacy',
        movementListMenu: 'movement_list_ansible_legacy',
        targetHostMenu: 'target_host_ansible_legacy',
        substValueMenu: 'subst_value_list_ansible_legacy',
        executionListMenu: 'execution_list_ansible_legacy'
    },
    check_operation_status_ansible_pioneer: {
        movementType: 'Ansible Pioneer',
        movementGem: 'AP',
        movementClassName: 'node-ansible-pioneer',
        movementListMenu: 'movement_list_ansible_pioneer',
        targetHostMenu: 'target_host_ansible_pioneer',
        substValueMenu: 'subst_value_list_ansible_pioneer',
        executionListMenu: 'execution_list_ansible_pioneer'
    },
    check_operation_status_terraform_cloud_ep: {
        movementType: 'Terraform Cloud/EP',
        movementGem: 'TERE',
        movementClassName: 'node-terraform-cloud-ep',
        movementListMenu: 'movement_list_terraform_cloud_ep',
        targetHostMenu: '',
        substValueMenu: 'subst_value_list_terraform_cloud_ep',
        executionListMenu: 'execution_list_terraform_cloud_ep'
    },
    check_operation_status_terraform_cli: {
        movementType: 'Terraform CLI',
        movementGem: 'TERC',
        movementClassName: 'node-terraform-cli',
        movementListMenu: 'movement_list_terraform_cli',
        targetHostMenu: '',
        substValueMenu: 'subst_value_list_terraform_cli',
        executionListMenu: 'execution_list_terraform_cli'
    }
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   履歴管理
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    履歴保存（AIサービス側の会話へ保存）
##################################################
*/
// 会話履歴をプラットフォーム側の会話（conversations）へ保存する。
// 応答ループの途中から何度も呼ばれるため、チャットごとにキューを持ち、
// 常に最新の1件だけを実行する（古い保存要求は破棄、実行中のものは中断する）。
//
// メッセージの送信時はプラットフォーム側が履歴を自動保存するため、この保存は
// 画面表示用の情報（_displayText / _attachments 等）を含む正の履歴を残すためのもの。
async historyEnqueue() {
    const llm = this.llm;
    if ( !llm ) return;
    // 履歴が空（画面を開いただけ）なら、空の会話を残さないため保存しない。
    const history = llm.getChatHistory();
    if ( !history || !history.length ) return;

    let state = this.historyQueues.get( this.chatId );
    if ( !state ) {
        state = {
            tail: Promise.resolve(),
            version: 0,
            controller: null
        };
        this.historyQueues.set( this.chatId, state );
    }

    // 新しい保存要求が来るたびに番号を増やす。（最新のversionだけを実行する。）
    state.version += 1;
    const requestVersion = state.version;
    // 実行中の保存があれば中断して最新だけを通す（保存は履歴の全置換なので、
    // 最新の1回だけ完走すればよい）。
    if ( state.controller ) {
        state.controller.abort();
    }

    const current = state.tail
        // 前の処理が失敗しても、後続は実行可能にする
        .catch( error => {
            if ( error.name !== 'AbortError') console.error('Previous save failed:', error );
        })
        .then(async () => {
            // 自分より新しい保存要求が存在する場合、この処理は古いので実行しない。
            if ( requestVersion !== state.version ) {
                return {
                    status: 'skipped',
                    reason: 'A newer save request exists.'
                };
            }
            // AbortController
            const controller = new AbortController();
            state.controller = controller;

            try {
                await llm.saveHistory( controller.signal );

                // 中断再開マーカーを更新する。初回保存で会話IDが確定するため、
                // 実行中に閉じられても、この会話IDから履歴を取得して自動再開できる。
                // （このstateが現在表示中の会話のときだけ更新する）
                if ( this.historyQueues?.get?.( this.chatId ) === state ) {
                    this._writeActiveChat( this.isRunning );
                }

                return {
                    status: 'done',
                    id: llm.conversationId
                };
            } catch ( error ) {
                if ( error.name === 'AbortError') {
                    return {
                        status: 'aborted'
                    };
                }
                throw error;
            } finally {
                // 別の処理がcontrollerを置き換えている可能性があるため、自分のcontrollerの場合だけ解除する。
                if ( state.controller === controller ) {
                    state.controller = null;
                }
            }
        });

    state.tail = current;
    return current;
}
// 履歴（LLMメッセージ配列）からチャット表示を再構築する共通処理。
// 履歴復元（resumeChat）と会話の巻き戻し（rewindConversation）で共用する。
// 表示のみを行い、LLM履歴（setChatHistory）や chatId / 会話IDの管理は呼び出し側で行う。
// 戻り値：tool_use_id → tool_result の対応表（呼び出し側の後処理で使う）。
_renderChatHistory( history ) {
    this.clearFile();
    // 破棄する吹き出しの画像プレビュー（objectURL）を解放する。
    this.revokeAttachmentPreviews();
    this.initChatArea();

    // 更新されたページのリンクを再構築するため、控えを初期化する。
    this._turnUpdatedMenus = new Map();

    // ドライバー実行画面の復元用に、tool_use_id → tool_result を先に集める
    // （tool_result は tool_use の次の user メッセージに入っているため）
    const toolResultMap = this.collectToolResults( history );

    // 選択肢（ask_user_choice 等の uiTools）の tool_use_id を集めておく。
    // これらに対応する tool_result は、ユーザの回答テキストとして復元表示する。
    const choiceToolIds = this.collectChoiceToolIds( history );

    for ( let blockIndex = 0; blockIndex < history.length; blockIndex++ ) {
        const block = history[ blockIndex ];
        const content = block.content ?? [];
        if ( fn.typeof( content ) === 'array' && block.role ) {
            for ( const item of content ) {
                const type = item.type;
                if ( type === 'text') {
                    // ユーザメッセージはひとつ前の応答の区切り。ここまでに更新された
                    // ページのリンクを、ライブ時と同じ位置（応答の末尾）に復元表示する。
                    if ( block.role === 'user') this.renderUpdatedMenuLinks( false );
                    // ユーザメッセージに表示用の別文言（_displayText）が保存されていれば、
                    // 本文（LLMへ送った指示文）ではなくそちらを吹き出しに復元する。
                    const restoredText = ( block.role === 'user'
                        && typeof block._displayText === 'string' && block._displayText !== '')
                        ? block._displayText
                        : ( item.text ?? '');
                    // システム操作（会話終了など）として送信されたユーザターンは、
                    // 復元時もシステム通知として表示する。
                    const restoredRole = ( block.role === 'user' && block._displaySystem === true )
                        ? 'system'
                        : block.role;
                    const message = {
                        role: restoredRole,
                        text: restoredText,
                        // 添付ファイルのメタ情報を復元（userメッセージのみ持つ）
                        attachments: block._attachments,
                        // 発言時刻を復元（保存済みの _timestamp。無ければ時刻は表示しない）
                        timestamp: block._timestamp
                    };
                    // システム通知ではない通常のユーザ発言は巻き戻しの起点にできる。
                    // 対応する履歴ブロックの位置（blockIndex）を持たせ、巻き戻しボタンを表示する。
                    if ( restoredRole === 'user') {
                        message.rewindable = true;
                        message.historyIndex = blockIndex;
                    }
                    this.updateChat( message, false );
                } else if ( type === 'tool_use' && block.role === 'assistant') {
                    const uiTool = this.uiTool( item.name );
                    if ( uiTool ) {
                        // 画面専用ツール（HTML表示・選択肢など）は、保存された input から
                        // それぞれのツール自身が表示を復元する。
                        uiTool.resume( item, block );
                    } else {
                        // execute-driver / dryrun-driver は専用の実行画面を復元する
                        this.resumeDriverExecution( item, toolResultMap.get( item.id ));
                        // maintenance-all / create-menu なら更新先メニューを控える
                        this.collectUpdatedMenuFromHistory( item, toolResultMap.get( item.id ));
                    }
                } else if ( type === 'tool_result' && choiceToolIds.has( item.tool_use_id ) ) {
                    // 選択肢への回答は応答の区切り。ここまでの更新ページのリンクを先に表示する。
                    this.renderUpdatedMenuLinks( false );
                    // 選択肢への回答は tool_result として保存されているため、
                    // ユーザメッセージとして復元表示する（送信時と同じ見た目）。
                    // この位置まで巻き戻すと直前の選択肢が未応答（回答待ち）状態に戻るため、
                    // 巻き戻し起点にできる。対応する履歴ブロックの位置を持たせる。
                    this.updateChat({
                        role: 'user',
                        text: this.extractChoiceAnswerText( item ),
                        timestamp: block._timestamp,
                        rewindable: true,
                        historyIndex: blockIndex,
                    }, false );
                }
            }
        }
    }

    // 最後のターンで更新されたページのリンクを表示する（以降にユーザメッセージが無いため）。
    this.renderUpdatedMenuLinks( false );

    return toolResultMap;
}
// 履歴から再開
// conversationId … 復元元の会話ID（プラットフォーム側の会話）。この会話へ続きを保存する。
async resumeChat( history, conversationId ) {
    if ( fn.typeof( history ) !== 'array' ) {
        throw new Error('履歴の形式が不正です。');
    }
    if ( fn.typeof( conversationId ) !== 'string') {
        throw new Error('会話IDの形式が不正です。');
    }
    // 復元した履歴を引き継ぐLLM層を用意する
    const llm = await this.ensureLlm();
    if ( !llm ) {
        throw new Error('ご利用の準備が完了していないため、会話を再開できません。');
    }
    const toolResultMap = this._renderChatHistory( history );

    this.pendingChoiceToolId = null;
    this.restorePendingChoice( history, toolResultMap );

    // 再開ごとに新しいchatIdを採番し、独立した保存state（historyQueues）を持たせる。
    // これをしないと、再開前のチャットのstate（実行中の保存要求）を引き継いでしまう。
    this.chatId = this.chatIdCounter++;
    // 復元元の会話を引き継ぐ（新しい会話は作らず、続きをこの会話へ保存する）
    llm.attachConversation( conversationId, history );

    // 中断された会話の自己修復：
    // インクリメンタル保存や離脱時保存により、履歴末尾が「tool_result 未応答の tool_use」で
    // 終わっている（＝ツール実行途中で閉じられた）ことがある。この状態のまま次の送信を行うと
    // 「tool_use に対応する tool_result が無い」API エラーになる。どの再開経路（会話履歴タブ／
    // 自動再開）でも安全に続けられるよう、ここでプレースホルダの tool_result を補って整合させる。
    const unansweredIds = this.getUnansweredToolUseIds( history );
    if ( unansweredIds.length ) {
        const placeholders = unansweredIds.map(( id ) => this._makeInterruptedToolResult( id ) );
        if ( this.pendingChoiceToolId ) {
            // 選択肢の回答待ちに、選択肢以外の未応答ツールが混在するケース。
            // ここでは履歴へ積まず退避し、ユーザーが選択肢に回答したときに選択肢の
            // tool_result と同じ user ターンでまとめて返す（1メッセージで全 tool_use に応答）。
            this.pendingToolResults = placeholders;
        } else {
            // ツール実行途中で中断。プレースホルダの tool_result を履歴へ確定して整合させる。
            llm.appendToolResults( placeholders );
        }
    }

    // 復元した会話を中断再開マーカーに紐付ける（まだ実行中ではない）。
    // この後で実際にターンが走れば _runResponseLoop が running=true に更新する。
    this._writeActiveChat( false );

    // 読込完了後、一番下までスクロールする（レイアウト確定を待つ）
    requestAnimationFrame(() => {
        const chatArea = this.elements.bodyInner;
        chatArea.scrollTop = chatArea.scrollHeight;
    });
}
/*
##################################################
    会話の巻き戻し
##################################################
*/
// 指定した履歴ブロック（ユーザメッセージ）の位置まで会話を巻き戻す。
// その位置以降（当該ユーザ発言とそれに続く応答すべて）を会話履歴・画面から取り除き、
// 取り除いたユーザ発言のテキストは入力欄に戻して、編集・再送信できるようにする。
// 注意：ITA（Exastro）側で実際に行われた作業（メニュー作成・更新、ドライバー実行など）は
//       巻き戻せない。会話（表示とLLM履歴）のみが巻き戻る。
async rewindConversation( historyIndex ) {
    if ( this.isRunning ) return;
    if ( !Number.isInteger( historyIndex ) || historyIndex < 0 ) return;

    const llm = this.llm;
    const history = ( llm && typeof llm.getChatHistory === 'function' ) ? llm.getChatHistory() : null;
    if ( !Array.isArray( history ) || historyIndex >= history.length ) return;

    // 巻き戻しの起点となるユーザ発言のテキスト（入力欄に戻す用）。
    // 通常発言は text ブロック、選択肢への回答は tool_result なのでその内容を取り出す。
    const removedBlock = history[ historyIndex ];
    let removedText = '';
    if ( removedBlock && Array.isArray( removedBlock.content ) ) {
        const textItem = removedBlock.content.find(( item ) => item.type === 'text' );
        if ( textItem && typeof textItem.text === 'string' ) {
            removedText = textItem.text;
        } else {
            const toolResultItem = removedBlock.content.find(( item ) => item.type === 'tool_result' );
            if ( toolResultItem ) removedText = this.extractChoiceAnswerText( toolResultItem );
        }
    }

    // 実行済みのITA作業が元に戻らない旨を明示して確認する。
    const ok = window.confirm(
        'この時点まで会話を巻き戻します。これより後のやりとりは会話から削除されます。\n\n'
        + '【ご注意】ここまでにITA（Exastro）で実際に行われた作業（メニューの作成・更新、'
        + 'ドライバー実行など）は元に戻りません。巻き戻るのは会話の表示とAIの記憶（会話履歴）のみです。\n\n'
        + '巻き戻してよろしいですか？'
    );
    if ( !ok ) return;

    // LLM履歴を起点の直前まで切り詰める
    const truncated = history.slice( 0, historyIndex );
    if ( typeof llm.setChatHistory === 'function' ) llm.setChatHistory( truncated );

    // 途中で切ったため、選択肢・退避中ツール結果などの保留状態はすべて破棄する。
    this.pendingChoiceToolId = null;
    this.pendingExtraChoiceToolIds = [];
    this.pendingToolResults = [];

    // 表示を作り直す（現在の会話を継続するため、chatId と会話IDは維持する）
    const toolResultMap = this._renderChatHistory( truncated );
    // 切り詰めた末尾が未応答の選択肢で終わっていれば、その保留状態（回答待ち）を復元する。
    // これにより、次のユーザ入力がその選択肢に対する tool_result として返り、会話を継続できる。
    this.restorePendingChoice( truncated, toolResultMap );

    // 選択肢の回答時点まで巻き戻した場合、同じ応答に含まれていた「通常ツール」の tool_use も
    // 未応答のまま残る。次回送信で「tool_use に対応する tool_result が無い」API エラーに
    // ならないよう、選択肢以外の未応答 tool_use にはプレースホルダの結果を持たせておく。
    if ( this.pendingChoiceToolId ) {
        const choiceIds = new Set([ this.pendingChoiceToolId, ...( this.pendingExtraChoiceToolIds ?? []) ]);
        const placeholders = [];
        for ( const id of this.getLastAssistantToolUseIds() ) {
            if ( choiceIds.has( id ) ) continue;
            placeholders.push({
                type: 'tool_result',
                tool_use_id: id,
                content: '（会話の巻き戻しにより、この操作の結果は破棄されました）'
            });
        }
        this.pendingToolResults = placeholders;
    }

    // 取り除いたユーザ発言を入力欄に戻し、そのまま編集・再送信できるようにする。
    if ( this.elements.message ) {
        this.elements.message.value = removedText;
        this.elements.message.focus();
    }

    // 保存されている履歴も切り詰めた内容へ置き換える。
    // 通常の送信ではプラットフォーム側が履歴を自動保存するため保存しなおしは不要だが、
    // 巻き戻しは画面側だけを切り詰めるため、ここで保存しなおさないと巻き戻した後のやりとりが
    // 巻き戻す前の履歴の続きになってしまう。
    // 失敗しても画面の巻き戻し自体は成立しているため、次の送信時の再同期に任せて続行する。
    try {
        await llm.saveHistory();
    } catch ( error ) {
        console.warn( error );
    }

    // 一番下までスクロール
    requestAnimationFrame(() => {
        const chatArea = this.elements.bodyInner;
        if ( chatArea ) chatArea.scrollTop = chatArea.scrollHeight;
    });
}
// 履歴全体から tool_use_id → tool_result の対応表を作る
// （tool_result は tool_use を含む assistant メッセージの次の user メッセージにある）
collectToolResults( history ) {
    const map = new Map();
    for ( const block of history ) {
        const content = block.content ?? [];
        if ( fn.typeof( content ) !== 'array') continue;
        for ( const item of content ) {
            if ( item.type === 'tool_result' && item.tool_use_id ) {
                map.set( item.tool_use_id, item );
            }
        }
    }
    return map;
}
// 履歴全体から、選択肢ツール（uiTools）の tool_use の id 集合を作る。
// この id を tool_use_id に持つ tool_result は、ユーザの回答として復元表示する。
collectChoiceToolIds( history ) {
    const ids = new Set();
    for ( const block of history ) {
        if ( block.role !== 'assistant') continue;
        const content = block.content ?? [];
        if ( fn.typeof( content ) !== 'array') continue;
        for ( const item of content ) {
            if ( item.type === 'tool_use' && this.isUiChoiceTool( item.name ) && item.id ) {
                ids.add( item.id );
            }
        }
    }
    return ids;
}
// 選択肢の tool_result からユーザの回答テキストを取り出す。
// content は文字列、またはテキストブロックの配列のことがある。
extractChoiceAnswerText( toolResult ) {
    const content = toolResult?.content;
    if ( typeof content === 'string') return content;
    if ( Array.isArray( content ) ) {
        return content
            .map(( item ) => ( typeof item === 'string' ? item : ( item?.text ?? '') ) )
            .join('');
    }
    return '';
}
// LLM履歴の末尾にある assistant メッセージが持つ tool_use の id 集合を返す。
// tool_result を送る前に、対応する tool_use が本当に直前 assistant に存在するかを
// 検証するために使う（存在しない id への tool_result は API エラーになるため）。
getLastAssistantToolUseIds() {
    const ids = new Set();
    const llm = this.llm;
    const messages = ( llm && typeof llm.getChatHistory === 'function' ) ? llm.getChatHistory() : null;
    if ( !Array.isArray( messages ) ) return ids;
    // 末尾から最初に見つかる assistant メッセージを対象にする。
    for ( let i = messages.length - 1; i >= 0; i-- ) {
        const block = messages[ i ];
        if ( block.role !== 'assistant') continue;
        const content = Array.isArray( block.content ) ? block.content : [];
        for ( const item of content ) {
            if ( item && item.type === 'tool_use' && item.id ) ids.add( item.id );
        }
        break;
    }
    return ids;
}
// 履歴の末尾が「未応答の ask_user_choice（選択肢）tool_use」で終わっている場合に、
// その tool_use_id を pendingChoiceToolId に復元する。
// これにより、履歴復元後の最初の入力もボタン選択と同様に tool_result として返せる。
restorePendingChoice( history, toolResultMap ) {
    // 末尾から最初に見つかった assistant の tool_use を調べる。
    // それが選択肢ツールで、かつ対応する tool_result がまだ無ければ pending とみなす。
    for ( let i = history.length - 1; i >= 0; i-- ) {
        const block = history[ i ];
        const content = block.content ?? [];
        if ( fn.typeof( content ) !== 'array') continue;
        // user メッセージに tool_result が含まれていれば、直前の tool_use は応答済み。
        if ( block.role === 'user') {
            const hasToolResult = content.some(( item ) => item.type === 'tool_result');
            if ( hasToolResult ) return;
            continue;
        }
        if ( block.role !== 'assistant') continue;
        // この assistant ターンの選択肢ツール（uiTools）のうち、未応答のものを集める。
        // フォーマット崩れで1ターンに複数の選択肢 tool_use が出ることがあるため、
        // 先頭を代表（pendingChoiceToolId）、残りを pendingExtraChoiceToolIds に復元する。
        const unansweredChoiceIds = [];
        let hasToolUse = false;
        for ( const item of content ) {
            if ( item.type !== 'tool_use') continue;
            hasToolUse = true;
            if ( this.isUiChoiceTool( item.name ) && !toolResultMap.has( item.id ) ) {
                unansweredChoiceIds.push( item.id ?? '');
            }
        }
        if ( unansweredChoiceIds.length ) {
            this.pendingChoiceToolId = unansweredChoiceIds[ 0 ];
            this.pendingExtraChoiceToolIds = unansweredChoiceIds.slice( 1 );
        }
        // この assistant ターンに tool_use があれば、それが直近の未応答対象。ここで確定。
        if ( hasToolUse ) return;
    }
}
// 履歴復元時に execute-driver / dryrun-driver の実行画面（Movementノード）を再描画する。
// toolUse: 履歴内の tool_use ブロック（name, arguments を持つ）
// toolResult: 対応する tool_result ブロック（無い場合あり）
resumeDriverExecution( toolUse, toolResult ) {
    const DRIVER_TOOLS = ['execute-driver', 'dryrun-driver'];
    if ( !DRIVER_TOOLS.includes( toolUse.name )) return;

    // 実行メニュー（execution_*）→ ステータス確認メニュー（check_operation_status_*）へ変換
    const execMenu = toolUse.arguments?.menu ?? toolUse.input?.menu ?? '';
    const statusMenu = execMenu.startsWith('execution_')
        ? execMenu.replace(/^execution_/, 'check_operation_status_')
        : execMenu;
    if ( !this.drivers[ statusMenu ]) return;

    const movementName = toolUse.arguments?.movement_name ?? toolUse.input?.movement_name ?? '';
    const operationName = toolUse.arguments?.operation_name ?? toolUse.input?.operation_name ?? '';
    const resultData = this.extractDataFromResult( toolResult );
    const executionNo = resultData?.execution_no ?? '';
    const resultDataName = `ResultData_${executionNo}.zip`;
    const execListMenu = this.drivers?.[ statusMenu ]?.executionListMenu ?? '';

    // 実行画面のバブルを生成
    const el = this.createAssistantMessageElement('', false );
    const movement = this.movementElement( statusMenu, execListMenu, movementName, operationName, executionNo );
    el.querySelector('.aiAssistantChatAssistantMessageInner').replaceChildren( movement );

    // 直前がアシスタントなら連続クラスを付与
    const prevItem = this.elements.chatList.lastElementChild;
    if ( prevItem?.classList.contains('aiAssistantChatAssistantMessage')) {
        el.classList.add('aiAssistantChatAssistantMessageChain');
    }
    this.elements.chatList.append( el );

    // tool_result から最終ステータスを取り出して反映（①で付与した driver_execution を優先）
    const finalStatus = this.extractFinalStatusFromResult( toolResult );
    if ( finalStatus ) {
        this.updateToolProgress( el, finalStatus, true, resultDataName );
    } else {
        // 最終ステータスが無い＝確定しないまま中断された。このまま放置すると「待機中」スピナーが
        // 回り続けて固まって見えるため、停止表示に切り替える。
        // ・tool_result 自体が無い（ツール呼び出し途中でページを閉じた）＝ページ離脱による中断。
        // ・tool_result はあるが最終ステータスが取れていない＝監視が確定前に終了した。
        this.markDriverExecutionInterrupted( el, { hasToolResult: !!toolResult, executionNo } );
    }
}
// 実行状況が確定しないまま中断された Movement 実行バブルを「停止」表示に切り替える。
// ・「待機中」スピナーを止め、指定メッセージに差し替える。
// ・サーバ側で実行が継続・完了している可能性があるため、状態確認は押せるようにしておく。
markDriverExecutionInterrupted( runningEl, opts = {} ) {
    if ( !runningEl ) return;
    const waitingEl = runningEl.querySelector('.movementWaiting');
    const statusCheckButton = runningEl.querySelector('.movementStatusCheckButton');
    const emergencyStopButton = runningEl.querySelector('.movementEmergencyStopButton');
    const nodeEl = runningEl.querySelector('.node');

    // 実行No.は引数優先、無ければ状態確認ボタンの data 属性から拾う。
    // 実行No.が無い＝ツール呼び出し途中でページを閉じ、実行No.が記録されていない場合は
    // この画面から作業状態を確認できないため、ボタンを非活性化し文言もその旨にする。
    const executionNo = opts.executionNo || statusCheckButton?.dataset.executionNo || '';
    const canCheckStatus = !!executionNo;

    let messageHtml;
    if ( !canCheckStatus ) {
        messageHtml = 'ページ離脱により停止しました。<br>実行No.が記録されていないため、この画面からは作業状態を確認できません。'
            + 'サーバ側で実行が継続・完了している場合があるため、実行履歴の一覧などから状況をご確認ください。';
    } else if ( !opts.hasToolResult ) {
        messageHtml = 'ページ離脱により停止しました。<br>サーバ側で実行が継続・完了している場合があります。「作業状態確認」で最新の状況をご確認ください。';
    } else {
        messageHtml = '実行状況を確定できないまま終了しました。<br>「作業状態確認」で最新の状況をご確認ください。';
    }

    if ( waitingEl ) {
        waitingEl.classList.add('movementWaitingStopped');
        waitingEl.innerHTML =
            `<div class="movementStopped">${fn.html.icon('circle_exclamation')}`
            + `<span>${messageHtml}</span></div>`;
    }
    // 実行No.があるときだけ状態確認を活性化。緊急停止は常に不可（このセッションでは監視していない）。
    if ( statusCheckButton ) statusCheckButton.disabled = !canCheckStatus;
    if ( emergencyStopButton ) emergencyStopButton.disabled = true;
    // ノードを「停止」見た目にする（実行アニメーションを止め、STOP バッジを表示）。
    if ( nodeEl ) {
        nodeEl.classList.remove('ready', 'running');
        nodeEl.classList.add('complete');
        const nodeResult = nodeEl.querySelector('.node-result');
        if ( nodeResult ) nodeResult.setAttribute('data-result-text', 'STOP');
    }
}
// 履歴の tool_result から最終ステータス文字列を取り出す。
// ①で付与した driver_execution.final_status を優先し、無ければ再帰探索でフォールバック。
extractFinalStatusFromResult( toolResult ) {
    if ( !toolResult ) return '';
    let parsed = toolResult.content;
    if ( typeof parsed === 'string') {
        try {
            parsed = JSON.parse( parsed );
        } catch ( e ) {
            return '';
        }
    }
    if ( !parsed || typeof parsed !== 'object') return '';

    // ①で付与した確定ステータス
    const fromDriver = parsed.driver_execution?.final_status;
    if ( typeof fromDriver === 'string' && fromDriver ) return fromDriver;

    // フォールバック: structuredContent 配下を再帰探索
    return this._extractDriverStatus( parsed.result?.structuredContent ?? {});
}
// 履歴の tool_result から data を取り出す。
// watchDriverProgress と同じく result.structuredContent.result.data を想定（ゆらぎに対応）。
extractDataFromResult( toolResult ) {
    if ( !toolResult ) return '';
    let parsed = toolResult.content;
    if ( typeof parsed === 'string') {
        try {
            parsed = JSON.parse( parsed );
        } catch ( e ) {
            return '';
        }
    }
    if ( !parsed || typeof parsed !== 'object') return '';

    const structured = parsed.result?.structuredContent ?? {};
    const apiResult = structured.result ?? {};
    const data = apiResult.data ?? apiResult;
    return data;
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   離脱時の中断保存 ＆ 再読込時の自動再開
//
////////////////////////////////////////////////////////////////////////////////////////////////////
// 「作業中の会話」をブラウザ（localStorage）に記録するためのキー。ユーザーごとに分ける。
// ページを閉じても残るため、開き直したときに中断された会話を特定して再開できる。
_activeChatKey() {
    return `aiAssistantActiveChat:${this.id ?? 'unknown'}`;
}
// 現在の会話を「実行中かどうか」とともに localStorage へ記録する。
// conversationId（プラットフォーム側の会話ID）は最初の送信・保存で確定する。
// running=true かつ conversationId 確定済みのときだけ、次回読込での自動再開の対象になる。
_writeActiveChat( running ) {
    try {
        const conversationId = this.llm?.conversationId ?? null;
        const payload = { conversationId, running: !!running, chatId: this.chatId };
        localStorage.setItem( this._activeChatKey(), JSON.stringify( payload ) );
    } catch ( error ) {
        // localStorage が使えない環境でも致命的ではない（自動再開が効かないだけ）。
        console.warn('中断再開マーカーの保存に失敗しました。', error );
    }
}
// 中断再開マーカーを削除する（新規チャット開始時など）。
_clearActiveChat() {
    try {
        localStorage.removeItem( this._activeChatKey() );
    } catch ( error ) {
        console.warn('中断再開マーカーの削除に失敗しました。', error );
    }
}
// 停止・エラー時に _runResponseLoop へ渡す「空の保留状態」。
_emptyPending() {
    return { pendingChoiceToolId: null, pendingExtraChoiceToolIds: [], pendingToolResults: [] };
}
// 履歴保存（historyEnqueue）を待たずに投げる際の安全ラッパー。
// 応答ループ中に何度も呼ぶため、保存失敗が未処理の Promise 拒否にならないよう握りつぶす
// （本当の整合性は、次の保存 or 復元時の自己修復で担保される）。
_enqueueHistorySafe() {
    try {
        const p = this.historyEnqueue();
        if ( p && typeof p.catch === 'function' ) p.catch(( error ) => console.warn('履歴の逐次保存に失敗しました。', error ) );
    } catch ( error ) {
        console.warn('履歴の逐次保存に失敗しました。', error );
    }
}
// 中断された tool_use に返す、プレースホルダの tool_result を作る。
// 実行済みかどうかは不明なため、再実行させず状況確認を促す文面にする。
_makeInterruptedToolResult( toolUseId ) {
    return {
        type: 'tool_result',
        tool_use_id: toolUseId,
        content: '（この操作はページ離脱により中断されました。サーバ側では既に実行された可能性があります。'
            + '同じ操作を安易に再実行せず、必要なら現在の状況を確認したうえでユーザーに報告してください。）'
    };
}
// 履歴末尾の assistant ターンに含まれる、未応答（tool_result が無い）かつ選択肢以外の
// tool_use の id を返す。履歴末尾が assistant であることが前提（＝直後に tool_result が無い）。
// 中断された（ツール実行途中で閉じられた）会話を継続する際、これらへプレースホルダの
// tool_result を返して履歴整合を保つために使う。
getUnansweredToolUseIds( history ) {
    if ( !Array.isArray( history ) || !history.length ) return [];
    const last = history[ history.length - 1 ];
    if ( !last || last.role !== 'assistant' || !Array.isArray( last.content ) ) return [];
    const ids = [];
    for ( const item of last.content ) {
        if ( item && item.type === 'tool_use' && item.id && !this.isUiChoiceTool( item.name ) ) {
            ids.push( item.id );
        }
    }
    return ids;
}
// 復元した会話が「継続できる中断状態」か、末尾から判定する。
//   toolUse     : 末尾 assistant に未応答の（選択肢以外の）tool_use がある（ツール実行途中で中断）
//   userPending : 末尾が user（テキスト or tool_result）＝ LLM 応答前に中断
//   none        : 末尾 assistant がテキストのみ＝応答は完了済み（継続不要）
_detectInterruptedContinuation( history ) {
    if ( !Array.isArray( history ) || !history.length ) return { type: 'none', ids: [] };
    const last = history[ history.length - 1 ];
    if ( !last ) return { type: 'none', ids: [] };
    if ( last.role === 'assistant' ) {
        const ids = this.getUnansweredToolUseIds( history );
        return ids.length ? { type: 'toolUse', ids } : { type: 'none', ids: [] };
    }
    if ( last.role === 'user' ) {
        return { type: 'userPending', ids: [] };
    }
    return { type: 'none', ids: [] };
}
// ページ再読込時、前回「作業中」に中断された会話があれば復元し、ユーザーの確認のうえ継続する。
// 戻り値：復元して画面を占有した場合 true（呼び出し側は newChatStart をスキップする）。
async _tryAutoResume() {
    // 設定未完了なら再開できない（LLM を用意できない）。
    if ( !this.checkAiAssistantSetting() ) return false;

    // 中断再開マーカーを読む。実行中フラグが立っていて会話IDが確定しているものだけが対象。
    let marker = null;
    try {
        marker = JSON.parse( localStorage.getItem( this._activeChatKey() ) || 'null' );
    } catch ( error ) {
        marker = null;
    }
    if ( !marker || marker.running !== true || !marker.conversationId ) return false;

    // AIサービス側（会話）に保存されている履歴を取得する（会話履歴タブの再開と同じ経路）。
    let history;
    try {
        history = await AiAssistantLlm.fetchHistory( marker.conversationId );
    } catch ( error ) {
        console.warn('自動再開: 履歴の取得に失敗しました。新規チャットを開始します。', error );
        // 取得に失敗したマーカーは残しても意味がないので消す。
        this._clearActiveChat();
        return false;
    }
    if ( fn.typeof( history ) !== 'array' || !history.length ) {
        this._clearActiveChat();
        return false;
    }

    // 新規チャット相当の初期化（チャットUI＝入力欄・送信/停止ボタンの構築、LLMセットアップ、
    // 学習事項の反映）を行ってから履歴を復元する。会話履歴タブからの手動再開と同じ順序で、
    // newChatStart で土台を作ってから resumeChat する（初期化を飛ばすと入力欄が無くなる）。
    // ※ newChatStart 内の setNewChat がマーカーを消すが、必要な値は marker に取得済みで、
    //   resumeChat 後に改めて書き戻されるため問題ない。
    try {
        await this.newChatStart();
        await this.resumeChat( history, marker.conversationId );
    } catch ( error ) {
        console.warn('自動再開: 会話の復元に失敗しました。新規チャットを開始します。', error );
        this._clearActiveChat();
        return false;
    }

    // 復元が終わったのでページ全体のローディング表示（#content の nowLoading）を解除する。
    // これをしないと、継続処理（LLMの応答待ち等）が終わるまでページがローディングのまま固まって見える。
    document.querySelector('#content')?.classList.remove('nowLoading');

    // 中断状態に応じた継続（確認ダイアログ＋LLMループ）は、ページ描画・他タブの初期化・
    // mount の完了を止めないよう、現在の実行を抜けてから走らせる。
    // （await すると mount がLLM応答の完了まで返らず、window.confirm もページ描画前に出てしまう）
    setTimeout( () => {
        this._offerResumeContinuation().catch(( error ) => console.warn('自動再開の継続に失敗しました。', error ) );
    }, 0 );
    return true;
}
// 復元済みの会話について、中断状態を判定し、ユーザーの確認を得てから継続する。
// ・選択肢の回答待ち  : 確認不要。上の選択肢に答えれば続く旨を案内するだけ。
// ・完了済み          : 継続不要。復元した旨を案内し、マーカーを実行中でないに更新する。
// ・継続可能（途中）  : 確認ダイアログを出し、「はい」で自動継続、「いいえ」で復元のみ。
async _offerResumeContinuation() {
    const llm = this.llm;
    const history = ( llm && typeof llm.getChatHistory === 'function' ) ? llm.getChatHistory() : null;

    // 選択肢の回答待ちで復元された場合は、ユーザーの回答を待つ（自動継続しない）。
    if ( this.pendingChoiceToolId ) {
        this.updateChat({ role: 'system', text: '前回の会話を復元しました。上の選択肢に回答すると、続きから再開できます。' });
        // 回答待ち＝実行中ではないので、マーカーを実行中でないに更新する。
        this._writeActiveChat( false );
        return;
    }

    const info = this._detectInterruptedContinuation( history );

    // 継続の必要がない（応答完了済み）場合は、復元した旨だけ伝える。
    if ( info.type === 'none' ) {
        this.updateChat({ role: 'system', text: '前回の会話を復元しました。' });
        this._writeActiveChat( false );
        return;
    }

    // ここへ来る時点で、tool_use 未応答は resumeChat で既にプレースホルダ補完済み
    // （＝末尾は user）。修復後に整合した履歴を保存しておく（この時点で再度閉じても壊れないように）。
    this._enqueueHistorySafe();

    // 中断された作業がある旨を表示し、継続するか確認する。
    this.updateChat({ role: 'system', text: '前回、作業の途中でページが閉じられました。' });
    const ok = window.confirm(
        '前回、中断された作業があります。続きから再開しますか？\n\n'
        + '「はい」を選ぶとAIが処理を再開します（ITA（Exastro）への操作やトークン消費が発生する場合があります）。\n'
        + '「いいえ」を選ぶと会話は復元された状態のままになり、手動で続けられます。'
    );

    if ( !ok ) {
        // 復元のみ。次回読込で再び自動再開しないよう、マーカーを実行中でないに更新する。
        this._writeActiveChat( false );
        return;
    }

    // 応答ループを継続モードで再開する（新規ユーザ発言は積まず、履歴末尾から続きを生成させる）。
    await this._runResponseLoop({
        sendPayload: null,
        uploadedFiles: [],
        turnStartEl: null,
        isRewindableUserTurn: false,
        firstSendOptions: undefined,
        savedPending: this._emptyPending(),
        continuation: true,
    });
}
// 中断・エラーで巻き戻されたターンの吹き出しに専用クラスを付与する。
// turnStartEl（このターンのユーザ発言）から chatList 末尾までを「中断ターン」として区別する。
markTurnAborted( turnStartEl ) {
    const list = this.elements.chatList;
    if ( !list || !turnStartEl ) return;
    // turnStartEl 以降（同ターンで追加された全吹き出し）にクラスを付ける
    let el = turnStartEl;
    while ( el ) {
        el.classList.add('aiAssistantChatItemAborted');
        el = el.nextElementSibling;
    }
}
// 直近の送信済みユーザメッセージに「停止」ラベルを付与する
markLastUserMessageStopped() {
    const items = this.elements.chatList?.querySelectorAll('.aiAssistantChatUserMessage');
    const lastUser = items?.length ? items[ items.length - 1 ] : null;
    if ( !lastUser || lastUser.querySelector('.aiAssistantChatUserMessageStopped') ) return;
    const label = document.createElement('p');
    label.classList.add('aiAssistantChatUserMessageStopped');
    label.innerText = '送信を停止しました';
    lastUser.querySelector('.aiAssistantChatItemInner')?.append( label );
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   イベント設定
//
////////////////////////////////////////////////////////////////////////////////////////////////////
// root配下でselectorに一致した要素だけをhandlerへ渡す委譲リスナー。
// whileRunning: true のときは応答処理中（isRunning）でも実行する（読み取り専用操作など）。
delegate( root, type, selector, handler, { whileRunning = false } = {} ) {
    root.addEventListener( type, ( e ) => {
        if ( !whileRunning && this.isRunning ) return;
        const target = e.target?.closest?.( selector );
        if ( !target || !root.contains( target ) ) return;
        return handler.call( this, e, target );
    }, { signal: this.ac.signal });
}
// data-type に対応するアクション定義（*EventActions）を実行する共通処理。
//   whileRunning: true … 応答処理中（isRunning）でも実行する（読み取り専用の操作など）
//   lockButton  : true … 実行中はボタンを無効化して連打を防ぐ
// 定義がないdata-typeは対象外として無視する。
async runEventAction( actions, target, e ) {
    const action = actions[ target.dataset.type ];
    if ( !action ) return;
    if ( this.isRunning && !action.whileRunning ) return;
    if ( action.lockButton ) target.disabled = true;
    try {
        await action.run( target, e );
    } finally {
        if ( action.lockButton ) target.disabled = false;
    }
}
/*
##################################################
    イベント登録
##################################################
*/
bindEvents() {
    this.bindHeaderEvents();
    this.bindBodyEvents();
    this.bindFooterEvents();
}
/*
##################################################
    Headerイベント
##################################################
*/
// 新しいチャット・チャット終了は応答処理中でも呼べるようにし（whileRunning）、
// 「応答中は実行できない」ことを各処理の中でユーザーへ伝える（無反応にしない）。
headerEventActions = {
    newChat: { lockButton: true, whileRunning: true, run:() => this.newChatEvent() },
    // チャット終了は応答完了までボタンの状態を自前で管理するため lockButton は使わない
    // （lockButton の後処理で、終了後に無効化したボタンが再活性化されてしまう）
    closeChat: { whileRunning: true, run:() => this.closeChatEvent() },
    aiAssistantSetting: { lockButton: true, run:() => this.aiAssistantSettingEvent() }
}
bindHeaderEvents() {
    this.delegate( this.elements.header, 'click', '.itaButton[data-type]',
        ( e, button ) => this.runEventAction( this.headerEventActions, button, e ), { whileRunning: true });
}
// 新しいチャット
// 会話中の場合は確認したうえで、ここまでの履歴を保存してから新規チャット画面へ戻す。
// 履歴はAIサービス側の会話に保存されているため、新しいチャットを始めても失われない。
async newChatEvent() {
    // 応答中に会話を差し替えると、進行中のツール実行の結果が新しいチャットへ混ざるため中止する。
    if ( this.isRunning ) {
        alert('AIが応答中のため、新しいチャットを開始できません。\n応答が終わるか、停止ボタンで中止してからお試しください。');
        return;
    }
    if ( this.newChat !== true ) {
        // 表示用の情報（発言時刻・表示文言など）を含む最新の履歴を保存しておく。
        // 失敗しても新規チャットの開始は妨げない（保存は応答完了時にも行われている）。
        try {
            await this.historyEnqueue();
        } catch ( error ) {
            console.warn('新しいチャットを開始する前の履歴保存に失敗しました。', error );
        }
    }
    await this.newChatStart();
}
// チャット終了
// ここまでのやりとりのまとめをAIに出力させて会話を締める。
// 終了後もメッセージを送信すれば会話は続けられる（送信時に終了ボタンが再活性化される）。
async closeChatEvent() {
    // 応答中はまとめを送れない（送信が二重になる）ため、終わるまで待ってもらう。
    if ( this.isRunning ) {
        alert('AIが応答中のため、チャットを終了できません。\n応答が終わるか、停止ボタンで中止してからお試しください。');
        return;
    }
    // まだ何も送信していない（新規チャット画面）場合は終了するものが無い
    if ( this.newChat === true || !this.llm?.getChatHistory()?.length ) return;

    const ok = window.confirm(
        'このチャットを終了します。\n\n'
        + 'ここまでの作業内容のまとめをAIが出力します。\n'
        + '（終了後もメッセージを送信すれば、この会話を続けられます）\n\n'
        + '終了してよろしいですか？'
    );
    if ( !ok ) return;

    // 終了操作中は再度押せないようにする（通常のメッセージ送信で再活性化される）
    if ( this.elements.closeChatButton ) this.elements.closeChatButton.disabled = true;

    // まとめの指示文はLLMへ送り、吹き出しには短い文言をシステム通知として表示する。
    const historyLength = this.llm?.getChatHistory()?.length ?? 0;
    await this.sendMessage(
        'このチャットを終了します。ここまでのやりとりを踏まえて、次の内容を簡潔にまとめてください。\n'
        + '1. 実施した作業（ITA（Exastro）で作成・更新したメニューやデータ、実行した作業）\n'
        + '2. その結果（成功・失敗、確認できたこと）\n'
        + '3. 未完了の作業や引き継ぎが必要な事項、注意点\n'
        + 'これ以降の作業はありません。新たな提案や質問はせず、まとめのみを出力してください。',
        {
            displayText: 'チャットを終了します。ここまでの内容をまとめます。',
            systemAction: true
        }
    );

    // まとめのターンが履歴に残っていれば終了できた。停止・エラーでターンが巻き戻された
    // 場合は終了できていないため、終了ボタンを戻して再度終了できるようにする。
    const closed = ( this.llm?.getChatHistory()?.length ?? 0 ) > historyLength;
    if ( closed ) {
        this.updateChat({ role: 'system', text: 'このチャットは終了しました。会話を続ける場合は、メッセージを送信してください。'});
    } else if ( this.elements.closeChatButton ) {
        this.elements.closeChatButton.disabled = false;
    }
}
// AIアシスタント設定
async aiAssistantSettingEvent() {
    await this.setting.open();
}
/*
##################################################
    Bodyイベント
##################################################
*/
// Body内のクリック操作（data-type単位）。
// 読み取り専用の操作（プレビュー・コピー・状態確認など）は whileRunning: true で
// 応答処理中でも実行できるようにしている。
bodyEventActions = {
    // 送信・停止
    send:   { lockButton: true, run:() => this.sendMessage( this.elements.message.value ) },
    choice: { lockButton: true, run:( button ) => this.sendMessage( button.innerText ) },
    stop:   { whileRunning: true, run:() => this.stopMessage() },

    // 添付ファイル
    file:              { lockButton: true, run:() => this.fileSelect() },
    fileRemove:        { lockButton: true, run:( button ) => this.removeFile( Number( button.dataset.index ) ) },
    fileEdit:          { lockButton: true, run:( button ) => this.editFile( Number( button.dataset.index ) ) },
    filePreview:       { lockButton: true, run:( button ) => this.previewFile( Number( button.dataset.index ) ) },
    // 吹き出し内の画像サムネイル（添付時と同じプレビューを開く）
    attachmentPreview: { whileRunning: true, run:( el ) => this.previewAttachment( el.dataset.previewUrl, el.dataset.filename ) },

    // 会話の巻き戻し
    rewindToHere: { lockButton: true, run:( button ) => this.rewindToHere( button ) },

    // Movement（作業実行）
    movementStatusCheck:    { whileRunning: true, run:( button ) => this.movementExecuteCheck( button ) },
    movementResultDownload: { whileRunning: true, run:( button ) => this.movementResultDownload( button ) },
    movementEmergencyStop:  { whileRunning: true, run:( button ) => this.movementStop( button ) },

    // コードブロック・表示専用HTML
    codeCopy:       { whileRunning: true, run:( button ) => this.copyCodeBlock( button ) },
    codeToInput:    { whileRunning: true, run:( button ) => this.setCodeBlockToInput( button ) },
    displayHtmlPdf: { whileRunning: true, run:( button ) => this.printDisplayHtmlAsPdf( button ) }
}
bindBodyEvents() {
    const body = this.elements.body;

    // クリック（bodyEventActionsで一括処理）
    this.delegate( body, 'click', '[data-type]',
        ( e, target ) => this.runEventAction( this.bodyEventActions, target, e ), { whileRunning: true });

    // 入力欄のキー操作（Enter送信・Alt+Enter改行）
    this.delegate( body, 'keydown', '.aiAssistantInputTextarea',
        ( e, textarea ) => this.inputKeydown( e, textarea ), { whileRunning: true });

    // 入力欄への貼り付け（画像はファイルとして添付する）
    this.delegate( body, 'paste', '.aiAssistantInputTextarea', ( e ) => this.pasteAttachment( e ) );

    // 添付ファイルのLLM送信トグル
    this.delegate( body, 'change', '[data-type="fileToggle"]',
        ( e, check ) => this.toggleFileLlm( Number( check.dataset.index ) ), { whileRunning: true });

    // 入力欄へのファイルドラッグ&ドロップ
    this.bindComposerDragEvents( body );

    // Movementノードのホバー表示・作業状態確認
    this.bindMovementNodeEvents( body );
}
// 入力欄のキーダウン
async inputKeydown( e, textarea ) {
    if ( e.key !== 'Enter') return;

    // Excelの癖（Alt+Enter／MacはOption+Enter）でも改行できるようにする。
    // Alt+Enterの既定動作はブラウザやOSで一定しないため、明示的に改行を挿入する。
    // Ctrl+Enterは他アプリで「送信」の意味が強いため割り当てない。
    if ( e.altKey && !e.ctrlKey && !e.metaKey ) {
        e.preventDefault();
        textarea.setRangeText('\n', textarea.selectionStart, textarea.selectionEnd, 'end');
        textarea.dispatchEvent( new Event('input', { bubbles: true }) );
        return;
    }

    // IME変換中の確定Enterで送信しないようにする。
    if ( e.isComposing || e.keyCode === 229 ) return;

    // Shift+Enterは改行（既定動作のまま）
    if ( e.shiftKey ) return;

    // Enterは送信ボタンのクリックと同じ処理を行う（連打防止のロックも共通）
    e.preventDefault();
    if ( this.isRunning ) return;
    const sendButton = this.elements.body.querySelector('.aiAssistantInputActionsSendButton');
    if ( sendButton ) await this.runEventAction( this.bodyEventActions, sendButton, e );
}
// 入力欄への貼り付け
// スクリーンショットやコピーした画像をペーストした場合、テキストではなく
// 添付ファイルとして扱う（ドラッグ&ドロップと同じ setFile 経路に流す）。
pasteAttachment( e ) {
    // クリップボード内の画像ファイルだけを取り出す。
    const imageFiles = Array.from( e.clipboardData?.items ?? [] )
        .filter(( item ) => item.kind === 'file' && ( item.type ?? '').startsWith('image/') )
        .map(( item ) => item.getAsFile() )
        .filter(( file ) => file )
        .map(( file ) => this.normalizePastedImageFile( file ) );
    if ( !imageFiles.length ) return;

    // 画像を添付として扱うため、テキストへの貼り付け（＝ゴミ文字混入）は抑止する。
    e.preventDefault();
    // 貼り付け画像は解析ONで追加する（そのままAIが読み取れるようにする）。
    this.setFile( imageFiles, { useLlm: true });
}
// 入力欄へのファイルドラッグ&ドロップ
// ドラッグの出入りは子要素をまたぐ度に発火するため、深度カウンタでちらつきを防ぐ。
bindComposerDragEvents( body ) {
    const composerSelector = '.aiAssistantChatComposer';
    // ファイル以外のドラッグ（テキスト選択など）は対象外
    const hasFiles = ( e ) => Array.from( e.dataTransfer?.types ?? [] ).includes('Files');
    const setDragover = ( composer, dragover ) => composer.classList.toggle('aiAssistantChatComposerDragover', dragover );
    let dragDepth = 0;

    this.delegate( body, 'dragenter', composerSelector, ( e, composer ) => {
        if ( !hasFiles( e ) ) return;
        e.preventDefault();
        dragDepth++;
        setDragover( composer, true );
    });
    this.delegate( body, 'dragover', composerSelector, ( e ) => {
        if ( !hasFiles( e ) ) return;
        // preventDefaultしないとdropが発火しない
        e.preventDefault();
        if ( e.dataTransfer ) e.dataTransfer.dropEffect = 'copy';
    });
    // ドラッグ解除・ドロップは、応答処理中でもドラッグ表示を必ず戻す
    this.delegate( body, 'dragleave', composerSelector, ( e, composer ) => {
        if ( !hasFiles( e ) ) return;
        dragDepth--;
        if ( dragDepth > 0 ) return;
        dragDepth = 0;
        setDragover( composer, false );
    }, { whileRunning: true });
    this.delegate( body, 'drop', composerSelector, ( e, composer ) => {
        if ( !hasFiles( e ) ) return;
        e.preventDefault();
        dragDepth = 0;
        setDragover( composer, false );
        if ( this.isRunning ) return;
        const files = Array.from( e.dataTransfer?.files ?? [] );
        if ( files.length ) this.setFile( files );
    }, { whileRunning: true });
}
// Movementノード（作業実行の進捗表示）
// クリックでの作業状態確認は bodyEventActions ではなく、data-type を持たない
// .node-result 自体が対象のためここで個別に登録する。
bindMovementNodeEvents( body ) {
    const nodeSelector = '.node-result';
    // mouseover／mouseoutは子要素をまたぐ度に発火するため、
    // .node-result内の移動（mouseenter／mouseleave相当）は無視する
    const isInnerMove = ( e, result ) => result.contains( e.relatedTarget );

    this.delegate( body, 'mouseover', nodeSelector, ( e, result ) => {
        if ( isInnerMove( e, result ) ) return;
        result.classList.add('mouseenter');
    }, { whileRunning: true });
    this.delegate( body, 'mouseout', nodeSelector, ( e, result ) => {
        if ( isInnerMove( e, result ) ) return;
        result.classList.remove('mouseenter');
    }, { whileRunning: true });
    this.delegate( body, 'click', nodeSelector, ( e, result ) => {
        this.movementExecuteCheck( result );
    }, { whileRunning: true });
}
// この吹き出し（ユーザ発言）の時点まで会話を巻き戻す
rewindToHere( button ) {
    const bubble = button.closest('.aiAssistantChatUserMessage');
    return this.rewindConversation( bubble ? Number( bubble.dataset.historyIndex ): NaN );
}
// コードブロックをクリップボードへコピーする
copyCodeBlock( button ) {
    // 連打防止：コピー直後の短い間は再実行しない
    if ( button.classList.contains('aiAssistantChatCodeButtonCopied') ) return;
    // 色は変えず、押した合図に少しだけ薄く表示する
    button.classList.add('aiAssistantChatCodeButtonCopied');
    setTimeout( () => button.classList.remove('aiAssistantChatCodeButtonCopied'), 800 );
    return this.copyToClipboard( this.getCodeBlockText( button ) );
}
// コードブロックの内容を入力欄へセットする（送信はしない）
setCodeBlockToInput( button ) {
    if ( !this.elements.message ) return;
    this.elements.message.value = this.getCodeBlockText( button );
    this.elements.message.focus();
}
/*
##################################################
    Footerイベント
##################################################
*/
// モデルの選択肢は普段隠れているため、モデル名のクリックで開閉する。
// フッターは更新のたびに作り直すため、イベントはフッターへ委譲して1度だけ設定する。
bindFooterEvents() {
    const footer = this.elements.footer;

    // 応答処理中でも選択肢は開けるようにする（実際の切り替えはselectModelで止める）
    this.delegate( footer, 'click', '.modelSelectedName', () => {
        this.toggleFooterModelList();
    }, { whileRunning: true });

    this.delegate( footer, 'change', '.modelSelectRadio', ( e, radio ) => {
        this.selectModel( radio.value );
    }, { whileRunning: true });

    // 使用中のモデルを選び直した場合はchangeが発生しないため、クリックでも閉じる
    this.delegate( footer, 'click', '.modelSelectLabel', () => {
        this.closeFooterModelList();
    }, { whileRunning: true });

    // 選択肢の外側をクリックしたら閉じる
    document.addEventListener('click', ( e ) => {
        if ( e.target?.closest?.('.modelSelectWrap') ) return;
        this.closeFooterModelList();
    }, { signal: this.ac.signal });
}
// モデルの選択肢の開閉
toggleFooterModelList() {
    this.elements.modelList?.querySelector('.modelSelectList')?.classList.toggle('modelSelectOpen');
}
closeFooterModelList() {
    this.elements.modelList?.querySelector('.modelSelectList')?.classList.remove('modelSelectOpen');
}
// 使用するモデルを切り替える
selectModel( modelId ) {
    this.closeFooterModelList();

    // 応答処理中の切り替えは、送信中のやり取りと表示が食い違うため受け付けない。
    // ラジオは操作した時点で切り替わっているので、使用中のモデルへ戻す。
    if ( this.isRunning || !modelId ) {
        this.updateFooterModelList();
        return;
    }

    // 切り替えたモデルは次の送信時にLLMへ反映する（会話は作り直さない）
    this.modelId = modelId;

    const modelName = this.setting.currentPickupModels.find(( item ) => item.id === modelId )?.name ?? '';
    const selectedName = this.elements.modelList?.querySelector('.modelSelectedName');
    if ( selectedName ) selectedName.innerText = modelName;
}
////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ユーティリティ
//
////////////////////////////////////////////////////////////////////////////////////////////////////
/*
##################################################
    トークン取得
##################################################
*/
getToken() {
    return ( fn.getCmmonAuthFlag() )? CommonAuth.getToken():
        ( window.parent !== window && window.parent.getToken )? window.parent.getToken(): null;
}
/*
##################################################
    スリープ
##################################################
*/
sleep( time ) {
    return new Promise( ( resolve ) => setTimeout( resolve, time ) );
}
/*
##################################################
    fetch リトライ
##################################################
*/
// fetch の応答エラー／ネットワークエラー時にリトライする共通処理（LLM・ツール実行で共用）。
// - AbortError（ユーザ都合の停止）はリトライせず即座に throw する。
// - 一時的なHTTPステータス（408 / 425 / 429 / 5xx）や fetch 例外（ネットワーク断）で再試行する。
// - 指数バックオフ（baseDelay を 2倍ずつ）で待機。Retry-After ヘッダがあればそれを優先し、
//   signal 経由で待機を即座に中断できる。
// - リトライを使い切った場合は最後の Response をそのまま返す（呼び出し側の .ok 判定を維持）。
static async fetchWithRetry( url, options = {}, retryOptions = {} ) {
    const retries = retryOptions.retries ?? 2;            // 追加試行回数（初回 + retries 回）
    const baseDelay = retryOptions.baseDelay ?? 1000;     // 初回リトライ前の待機（ミリ秒）
    const retryStatuses = retryOptions.retryStatuses ?? [ 408, 425, 429, 500, 502, 503, 504 ];
    const signal = options.signal;

    // signal が abort されたら待機を即座に打ち切る、リトライ待機用の sleep
    const wait = ( delay ) => new Promise(( resolve ) => {
        if ( signal?.aborted ) { resolve(); return; }
        const timer = setTimeout(() => {
            signal?.removeEventListener?.('abort', onAbort );
            resolve();
        }, delay );
        const onAbort = () => { clearTimeout( timer ); resolve(); };
        signal?.addEventListener?.('abort', onAbort, { once: true });
    });

    let lastError = null;
    for ( let attempt = 0; attempt <= retries; attempt++ ) {
        // 中断済みなら即座に AbortError
        if ( signal?.aborted ) {
            const err = new Error('Aborted');
            err.name = 'AbortError';
            throw err;
        }
        try {
            const response = await fetch( url, options );
            // 応答エラー（リトライ対象ステータス）で、まだ試行が残っていれば待機して再試行
            if ( retryStatuses.includes( response.status ) && attempt < retries ) {
                lastError = new Error(`HTTP ${response.status}`);
                // 待機時間：指数バックオフ。Retry-After ヘッダがあれば優先。
                let delay = baseDelay * Math.pow( 2, attempt );
                const retryAfter = response.headers?.get?.('Retry-After');
                if ( retryAfter ) {
                    const sec = Number( retryAfter );
                    if ( !Number.isNaN( sec ) ) delay = sec * 1000;
                }
                console.warn(`fetchWithRetry: 応答エラー HTTP ${response.status}。${delay}ms 後にリトライします（${attempt + 1}/${retries}）。`, url );
                await wait( delay );
                continue;
            }
            return response;
        } catch ( error ) {
            // ユーザ都合の停止はリトライしない
            if ( error?.name === 'AbortError' || signal?.aborted ) throw error;
            lastError = error;
            // 試行が残っていなければ throw（ネットワークエラーをそのまま呼び出し側へ）
            if ( attempt >= retries ) throw error;
            const delay = baseDelay * Math.pow( 2, attempt );
            console.warn(`fetchWithRetry: fetch 失敗。${delay}ms 後にリトライします（${attempt + 1}/${retries}）。`, url, error );
            await wait( delay );
        }
    }
    // ループを抜けるのは通常ないが、保険として最後のエラーを投げる
    if ( lastError ) throw lastError;
}

}