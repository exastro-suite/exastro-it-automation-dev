////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / ai_assistant_llm.js
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

// AIアシスタントのLLM層。
// チャット画面（AiAssistantChat）とプラットフォームAPIの会話（conversations）の間を受け持つ。
//
// ・認証情報（Credential）はプラットフォーム側に保存されており、ブラウザからは取得できないため、
//   LLMの呼び出しもプラットフォームAPI（/conversations/{id}/completions）を経由して行う。
// ・システムプロンプトとツール定義はプラットフォーム側が保持する（会話作成時に渡したtoolsと
//   prompt_profileが使われる）。
// ・会話履歴（メッセージのターン配列）は画面側（this.messages）を正とする。サーバー側にも履歴の
//   スナップショット（＝会話履歴の保存先そのもの）が保存されており、completionsはその保存内容を
//   使って問い合わせる。ITA側（会話履歴メニュー）への二重保存は行わない。
// ・テキストだけのユーザー発言は completions の message で送る。プラットフォーム側がユーザーターンと
//   AI応答を履歴へ自動保存するため、送信ごとの同期（PUT /messages）は不要。
// ・添付ファイル（image / document）やツール結果（tool_result）はmessage（文字列）では送れないため、
//   PUT /messages で履歴を全置換してから、messageなし（＝サーバー側は保存しない）で問い合わせる。
// ・ターンの区切り（ツール実行前・応答完了時など）と巻き戻しでは saveHistory() で全置換して保存する。
//   これで画面表示用の情報（_displayText / _attachments 等）を含む正の履歴が保存され、
//   completionsが積み上げるスナップショットも1件に圧縮される（復元時の取得が軽くなる）。
//   なお添付ファイルの実体（base64）は保存しない（復元は _attachments のメタ情報から行う）。
// ・サーバー側の履歴が画面側とずれているかは this.serverSynced で管理する。
// ・会話（プラットフォーム側のレコード）は最初の送信・保存のときに作成する（title は最初の発言から作る）。
//   画面を開いただけで空の会話が残らないようにするため、setup() では作成しない。
class AiAssistantLlm {
/*
##################################################
   REST API URL
##################################################
*/
static get apiUrl() {
    const { organizationId, workspaceId } = fn.getCommonParams();
    const conversation = `/api/${organizationId}/platform/workspaces/${workspaceId}/conversations`;
    return {
        // 会話: 作成 POST / 一覧 GET
        conversation: () => conversation,
        // 会話メッセージ: 取得 GET / 作成 POST / 全置換 PUT / 全削除 DELETE
        messages: ( conversationId ) => `${conversation}/${conversationId}/messages`,
        // AI応答の生成: POST
        completion: ( conversationId ) => `${conversation}/${conversationId}/completions`
    };
}
/*
##################################################
   定数
##################################################
*/
// システムプロンプトの切り替え（プラットフォーム側で読み込むプロンプトの種別）
static get promptProfile() {
    return 'AgenticAI';
}
// 会話タイトル（最初の発言からタイトルを作れなかった場合の既定値）
static get defaultTitle() {
    return 'タイトル無し';
}
// 会話タイトルの最大文字数（プラットフォーム側の TITLE カラムに合わせる）
static get titleLength() {
    return 256;
}
// 会話履歴（スナップショット）の取得件数。1回のGETで取得するレコード数。
//   保存（saveHistory）のたびに全置換され1件へ圧縮されるため、通常は1〜数件しか無い。
static get messagesFetchLimit() {
    return 100;
}
// 再送するHTTPステータス（一過性のエラーのみ。タイムアウトはユーザー確認のうえで再送する）
static get retryStatuses() {
    return [ 425, 429, 500, 502, 503 ];
}
// タイムアウトのHTTPステータス（待たされた末の再試行になるため、再送前にユーザーへ確認する）
static get timeoutStatuses() {
    return [ 408, 504 ];
}
/*
##################################################
   Constructor
##################################################
*/
constructor() {
    // 会話ID（最初の送信・保存のときに作成する。履歴復元時は復元元の会話IDを引き継ぐ）
    this.conversationId = null;
    // 会話履歴（Anthropic Messages API形式のターン配列）
    //   画面の表示・巻き戻し・サーバーへの履歴保存もこの配列を使う
    this.messages = [];
    // サーバー側に保存されている履歴が this.messages と一致しているか
    //   false のとき（巻き戻し・履歴復元・保存されない問い合わせの後など）は、
    //   次の問い合わせの前に PUT /messages で保存しなおす
    this.serverSynced = true;
    // 使用するAIサービス
    this.aiServiceId = '';
    // 使用するモデル（フッターで切り替えられる）
    this.modelId = '';
    // ツール定義（Anthropic tools形式）
    this.tools = [];
    // サーバー側の履歴を書き換える処理（全置換・completions）を直列化するためのキュー。
    // 保存（履歴の全置換）は応答ループから待たずに投げられるため、問い合わせと同時に走ると
    // サーバー側の履歴が壊れる（＝二重保存や、保存済み判定のずれ）。
    this.writeChain = Promise.resolve();
}
/*
##################################################
   Setup（AIサービス・モデル・ツールの設定）
##################################################
*/
// param = { aiServiceId, modelId }
// tools … MCPサーバーから取得したツール一覧（Anthropic tools形式へ変換して会話に登録する）
//
// 会話（プラットフォーム側のレコード）はここでは作らない。画面を開くたびに空の会話が
// 会話履歴に残るのを避けるため、最初の送信・保存のときに ensureConversation() で作成する。
async setup( param = {}, tools ) {
    this.aiServiceId = param.aiServiceId ?? '';
    this.modelId = param.modelId ?? '';
    this.tools = AiAssistantLlm.convertTools( tools );
    // 新しい会話なので、履歴と会話IDは初期化する（サーバー側も履歴が無いので同期済み）
    this.messages = [];
    this.conversationId = null;
    this.serverSynced = true;

    if ( !this.aiServiceId ) throw new Error('使用するAIサービスが選択されていません。');
    if ( !this.modelId ) throw new Error('使用するモデルが選択されていません。');
}
/*
##################################################
   会話（プラットフォーム側のレコード）
##################################################
*/
// 会話が未作成なら作成する。タイトルは更新できないため、最初の発言から作って登録する。
async ensureConversation() {
    if ( this.conversationId ) return this.conversationId;

    if ( !this.aiServiceId ) throw new Error('使用するAIサービスが選択されていません。');
    if ( !this.modelId ) throw new Error('使用するモデルが選択されていません。');

    const data = await this.request(AiAssistantLlm.apiUrl.conversation(), 'POST', {
        title: AiAssistantLlm.buildTitle( this.messages ),
        model_id: this.modelId,
        ai_service_id: this.aiServiceId,
        prompt_profile: AiAssistantLlm.promptProfile,
        // ツール定義は会話単位で固定される（completionsの都度は指定しない）
        tools: this.tools
    });

    this.conversationId = data.conversation_id ?? null;
    if ( !this.conversationId ) throw new Error('会話の作成に失敗しました。');

    return this.conversationId;
}
// 保存済みの会話を引き継ぐ（履歴復元）。復元元の会話へ続きを保存するため、新しい会話は作らない。
attachConversation( conversationId, history ) {
    if ( !conversationId ) throw new Error('会話IDが指定されていません。');
    this.conversationId = conversationId;
    this.setChatHistory( history );
}
// 会話のタイトルを作る。プラットフォーム側にタイトルの更新APIが無いため、会話の作成時に
// 決める必要がある。履歴内のユーザー発言のテキストを上限文字数まで結合し、タブと改行は取り除く。
static buildTitle( messages ) {
    let title = '';
    if ( Array.isArray( messages ) ) {
        for ( const turn of messages ) {
            if ( !turn || turn.role !== 'user' || !Array.isArray( turn.content ) ) continue;
            // 画面表示用の文言（システム操作など）があればそちらを優先する
            if ( typeof turn._displayText === 'string' && turn._displayText !== '') {
                title += turn._displayText;
            } else {
                for ( const block of turn.content ) {
                    if ( !block || block.type !== 'text' || typeof block.text !== 'string') continue;
                    title += block.text;
                    if ( title.length >= AiAssistantLlm.titleLength ) break;
                }
            }
            if ( title.length >= AiAssistantLlm.titleLength ) break;
        }
    }
    title = title.replace( /[\t\r\n]/g, '').slice( 0, AiAssistantLlm.titleLength );
    return ( title !== '')? title: AiAssistantLlm.defaultTitle;
}
/*
##################################################
   保存済みの会話履歴の取得（履歴復元用）
##################################################
*/
// 会話履歴（最新のスナップショット）を取得する。会話の作成前でも呼べるよう、
// APIを叩くためだけの一時インスタンスを使う。
static async fetchHistory( conversationId ) {
    if ( !conversationId ) throw new Error('会話IDが指定されていません。');
    const llm = new AiAssistantLlm();
    const limit = AiAssistantLlm.messagesFetchLimit;
    const endPoint = AiAssistantLlm.apiUrl.messages( conversationId );

    // 履歴はスナップショット（会話全体を丸ごと持つレコード）の列で、最後のレコードが最新。
    // 取得は message_seq の昇順・ページングのため、取得件数が上限に達している間は続きを読む。
    let history = [];
    for ( let offset = 0; ; offset += limit ) {
        const data = await llm.request(`${endPoint}?limit=${limit}&offset=${offset}`, 'GET');
        const messages = ( Array.isArray( data?.messages ) )? data.messages: [];
        if ( !messages.length ) break;
        const contents = messages[ messages.length - 1 ]?.contents;
        if ( Array.isArray( contents ) ) history = contents;
        if ( messages.length < limit ) break;
    }
    return history;
}
/*
##################################################
   保存済みの会話履歴の削除
##################################################
*/
// 会話に紐づくメッセージレコード（スナップショット）を全て削除する。
//
// 【制限事項】プラットフォームAPIに会話（conversations）自体を削除する口が無いため、
// 会話のレコードは残る（会話一覧には履歴が空の会話として残り続ける）。
// 会話ごと消すには DELETE /conversations/{conversation_id} の追加が必要。
static async deleteHistory( conversationId ) {
    if ( !conversationId ) throw new Error('会話IDが指定されていません。');
    const llm = new AiAssistantLlm();
    return await llm.request(AiAssistantLlm.apiUrl.messages( conversationId ), 'DELETE');
}
// MCPのツール定義（inputSchema）をAnthropic tools形式（input_schema）へ変換する
static convertTools( tools ) {
    if ( !Array.isArray( tools ) ) return [];
    return tools.map(( tool ) => {
        const { inputSchema, ...rest } = tool;
        if ( inputSchema !== undefined && rest.input_schema === undefined ) {
            rest.input_schema = inputSchema;
        }
        return rest;
    });
}
/*
##################################################
   使用するモデルの切り替え
##################################################
*/
// 会話のデフォルトモデルは会話作成時に決まるが、問い合わせごとに上書きできる。
setModel( modelId = '') {
    if ( modelId ) this.modelId = modelId;
}
/*
##################################################
   会話履歴
##################################################
*/
getChatHistory() {
    return this.messages;
}
// 画面側の履歴を差し替える（巻き戻し・履歴復元・ターンの巻き戻しなど）。
// サーバー側の保存内容とはずれるため、次の問い合わせの前に保存しなおす必要があるとマークする。
setChatHistory( history ) {
    this.messages = ( Array.isArray( history ) )? history: [];
    this.serverSynced = false;
}
/*
##################################################
   ツール結果を履歴へ確定（継続送信用）
##################################################
*/
// ツール実行結果（tool_result ブロック群）を user ターンとして履歴へ積む。
// 中断耐性のため、送信（send）を待たずにツール実行直後へ確定させ、その時点で保存できるようにする。
// この後のLLM呼び出しは send( null, null, signal, { alreadyPushed: true } ) で継続する。
appendToolResults( toolResults ) {
    if ( !Array.isArray( toolResults ) || !toolResults.length ) return;
    if ( !Array.isArray( this.messages ) ) this.messages = [];
    this.messages.push({
        'role': 'user',
        'content': toolResults,
        // 発言時刻（履歴保存・復元用。LLMには渡さない）
        '_timestamp': new Date().toISOString()
    });
    // サーバー側にはまだ無いターンなので、次の問い合わせの前に保存しなおす
    this.serverSynced = false;
}
/*
##################################################
   Send prompt
##################################################
*/
// prompt  … テキスト（文字列）または contentブロックの配列（tool_result等）
// files   … 送信するファイル（アップロード済みの情報。useLlm=trueのものは実体も渡す）
// signal  … 停止用のAbortSignal
// options … { displayText, systemAction, timestamp, alreadyPushed }
async send( prompt, files, signal, options = {} ) {
    // 継続送信（alreadyPushed）の場合、送るべきメッセージ（tool_result等）は呼び出し側が
    // 既に履歴へ積んでいるため、ここでは積まない。
    const alreadyPushed = options.alreadyPushed === true;
    // ユーザーターンを履歴へ積んだか（失敗時に取り消すため）
    let pushed = false;

    let data = null;
    let contents = null;
    // タイムアウトで再送したか（messageを指定した再送は、1度目が保存まで終わっていた場合に
    // サーバー側の履歴へ同じユーザーターンが二重に積まれる可能性があるため、同期済みとみなさない）
    let retried = false;
    try {
        // 履歴の全置換（保存）と問い合わせは、サーバー側の履歴を書き換える処理なので直列化する。
        data = await this.writeQueue( async () => {
            // ユーザーターンは書き込みキューの中で積む。先に積んでしまうと、待機中の保存が
            // 「まだ送信していないユーザーターン」を含む履歴を保存してしまい、その後に
            // messageを指定して問い合わせることで同じユーザーターンが二重に積まれる。
            let messageText = null;
            if ( !alreadyPushed ) {
                const userMessage = this.buildUserMessage( prompt, files, options );
                this.messages.push( userMessage );
                pushed = true;
                // completionsのmessage（文字列）で送れるユーザー発言か。テキスト1ブロックのみのターンが
                // 対象で、添付ファイルやツール結果を含むターンは送れない（→履歴を全置換して同期する）。
                messageText = AiAssistantLlm.completionMessageText( userMessage );
            }

            // 会話が未作成なら、ここで作成する（タイトルは積んだユーザー発言から作られる）
            await this.ensureConversation();

            if ( messageText !== null ) {
                // messageを指定した問い合わせは、プラットフォーム側がユーザーターンとAI応答を
                // 履歴へ自動保存する。サーバー側の履歴がずれている（巻き戻し・履歴復元後など）ときだけ、
                // 今回のユーザーターンを除いた履歴で全置換して整合させてから問い合わせる。
                if ( !this.serverSynced ) {
                    await this.syncHistory( signal, this.messages.slice( 0, -1 ) );
                }
            } else {
                // messageで送れないターン（tool_result・添付ファイル付きなど）は、
                // 問い合わせに使われるサーバー側の履歴を全置換して渡す。
                await this.syncHistory( signal );
            }

            try {
                return await this.requestCompletion( signal, messageText );
            } catch ( error ) {
                // タイムアウトは同じ内容の再送で解消することがあるため、ユーザーに確認して1度だけ再送する
                if ( !AiAssistantLlm.timeoutStatuses.includes( error?.status ) ) throw error;
                const proceed = window.confirm(
                    `応答がタイムアウトしました（HTTP ${error.status}）。\n`
                    + `もう一度試しますか？`
                );
                if ( !proceed ) throw new Error('タイムアウトのため、リトライを中止しました。');
                retried = true;
                return await this.requestCompletion( signal, messageText );
            }
        });
        contents = this.responseContents( data );
    } catch ( error ) {
        // 応答を得られなかったユーザーターンは履歴に残さない
        // （未応答のまま次の送信に混ざると、会話の整合性が崩れるため）
        if ( pushed ) this.messages.pop();
        // どこまでサーバーへ渡ったか（全置換の成否・保存の有無）が分からないため、
        // 次の問い合わせの前に保存しなおす
        this.serverSynced = false;
        throw error;
    }

    // saved=true なら、今回のユーザーターンとAI応答はサーバー側の履歴へ保存済み（＝同期されている）。
    // messageなしの問い合わせは保存されない（saved=false）ため、次の問い合わせの前に保存しなおす。
    this.serverSynced = ( data.saved === true && !retried );

    // 応答時刻（履歴保存・復元表示用。LLMには渡さない）。
    // 画面表示（呼び出し側）と一致させるため、返却する応答にも同じ値を載せる。
    const timestamp = new Date().toISOString();
    this.messages.push({
        'role': 'assistant',
        'content': contents,
        '_timestamp': timestamp,
        // この応答を生成したモデル（会話途中でモデルを変更できるため応答ごとに記録する）
        '_model': this.modelId
    });

    return {
        content: contents,
        stop_reason: data.stop_reason ?? null,
        usage: data.usage ?? null,
        _timestamp: timestamp,
        _model: this.modelId
    };
}
// completionsのmessageとして送れるユーザー発言なら、そのテキストを返す（送れないならnull）。
// messageはプラットフォーム側で { type: 'text', text: message } の1ブロックのユーザーターンとして
// 履歴へ保存されるため、それと同じ形のターン（テキスト1ブロックのみ・添付なし）だけを対象にする。
// ツール結果（tool_result）や添付ファイル（image / document、_attachmentsのメタ情報）を含むターンは
// messageでは表現できないので、履歴の全置換（PUT /messages）で渡す。
// 画面表示用の情報（_displayText / _displaySystem）を持つターンも、messageで送ると保存されずに
// 失われてしまうため、同様に全置換で渡す。
static completionMessageText( userMessage ) {
    if ( !userMessage || userMessage._attachments ) return null;
    if ( userMessage._displayText !== undefined || userMessage._displaySystem !== undefined ) return null;
    const content = userMessage.content;
    if ( !Array.isArray( content ) || content.length !== 1 ) return null;
    const block = content[0];
    if ( !block || block.type !== 'text' || typeof block.text !== 'string' || block.text === '') return null;
    return block.text;
}
/*
##################################################
   送信するユーザーターンの組み立て
##################################################
*/
buildUserMessage( prompt, files, options = {} ) {
    const fileList = ( Array.isArray( files ) )? files: ( files )? [ files ]: [];
    // 添付ファイルのメタ情報（履歴に保存し、復元に使う）
    const attachments = fileList.map(( file ) => {
        return {
            file_id: file.file_id ?? '',
            filename: file.filename ?? '',
            mime_type: file.mimeType || file.mime_type || '',
            size: file.size ?? '',
            use_llm: file.useLlm === true,      // ユーザーがAI解析をオンにしたか
            supported: file.supported === true  // LLMがネイティブに解析できる形式か
        };
    });

    let content = [];
    if ( typeof prompt === 'object' && prompt !== null ) {
        // ツールの実行結果（contentブロックの配列）
        content = prompt;
    } else {
        content.push({
            'type': 'text',
            'text': prompt
        });

        // useLlm=true のファイルはファイルの実体（base64）もcontentに追加する
        // Anthropic Messages API準拠：画像（image）とPDF（document）のみネイティブ添付できる
        const supportedImageTypes = [ 'image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        for ( const file of fileList ) {
            // 実体（base64のdata または 生テキストのtext）が無ければスキップ
            if ( !file.useLlm || ( !file.data && typeof file.text !== 'string') ) continue;
            const mimeType = file.mimeType || file.mime_type || '';
            if ( supportedImageTypes.includes( mimeType ) ) {
                // 画像
                content.push({
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': mimeType,
                        'data': file.data
                    }
                });
            } else if ( mimeType === 'application/pdf') {
                // PDF
                content.push({
                    'type': 'document',
                    'source': {
                        'type': 'base64',
                        'media_type': 'application/pdf',
                        'data': file.data
                    },
                    'title': file.filename ?? file.file_id ?? 'document'
                });
            } else if ( typeof file.text === 'string') {
                // テキストファイルは生テキストのドキュメントとして渡す
                content.push({
                    'type': 'document',
                    'source': {
                        'type': 'text',
                        'media_type': 'text/plain',
                        'data': file.text
                    },
                    'title': file.filename ?? file.file_id ?? 'document'
                });
            }
            // 上記以外の形式は実体を渡せない（file_idのメタ情報のみ）
        }
    }

    const userMessage = {
        'role': 'user',
        'content': content
    };
    // 添付があればメタ情報を持たせる（履歴保存・復元用。LLMへはメタ情報テキストとして渡す）
    if ( attachments.length ) {
        userMessage._attachments = attachments;
    }
    // 画面表示用の別文言があれば持たせる（履歴保存・復元用。LLMには渡さない）
    if ( typeof options.displayText === 'string' && options.displayText !== '') {
        userMessage._displayText = options.displayText;
    }
    // システム操作（会話終了など）としての表示種別を持たせる（同上）
    if ( options.systemAction === true ) {
        userMessage._displaySystem = true;
    }
    // 発言時刻（履歴保存・復元表示用）。画面表示と一致させるため、呼び出し側の時刻を優先する。
    userMessage._timestamp = ( typeof options.timestamp === 'string' && options.timestamp )
        ? options.timestamp
        : new Date().toISOString();

    return userMessage;
}
/*
##################################################
   会話履歴の保存（全置換）
##################################################
*/
// サーバー側の履歴を書き換える処理（全置換・completions・会話の作成）を直列化する。
// 保存（saveHistory）は応答ループから待たずに呼ばれるため、直列化しないと問い合わせ（send）と
// 同時に走り、「全置換 → completions」の間に別の全置換が割り込んで履歴が壊れる
// （ユーザーターンの重複など）。それを防ぐのがこのキューで、サーバー側の履歴を書き換える処理は
// すべて writeQueue() の中から呼ぶこと（＝ send と saveHistory 以外から呼ばない）。
writeQueue( task ) {
    const result = this.writeChain.then( task, task );
    // キューは後続の処理のために繋ぐだけ（エラーは呼び出し側で扱うため、ここでは伝播させない）
    this.writeChain = result.then( () => {}, () => {} );
    return result;
}
// 画面側の履歴をサーバーへ保存する（会話履歴の保存はこれだけで完結する）。
//   ・ターンの区切り（ツール実行前・応答完了時など）… 画面表示用の情報を含む正の履歴を残す
//   ・巻き戻し（会話の切り詰め）後 … 切り詰めた内容へ置き換える
// 会話が未作成で履歴も空の場合（画面を開いただけ）は、空の会話を残さないため何もしない。
async saveHistory( signal ) {
    return this.writeQueue( async () => {
        if ( !this.conversationId ) {
            if ( !this.messages.length ) return;
            await this.ensureConversation();
        }
        await this.syncHistory( signal, AiAssistantLlm.storableHistory( this.messages ) );
    });
}
// 保存する履歴に整える。添付ファイルの実体（image / document のbase64・生テキスト）は
// 肥大化するため保存しない（復元時は _attachments のメタ情報から表示を組み立てる）。
// 実体が無い場合は渡された配列をそのまま返す（＝保存後も「同期済み」を維持する）。
static storableHistory( messages ) {
    if ( !Array.isArray( messages ) ) return [];
    const dropTypes = [ 'image', 'document'];
    const isDropBlock = ( block ) => block && dropTypes.includes( block.type );
    const hasFileBody = messages.some(( turn ) => Array.isArray( turn?.content ) && turn.content.some( isDropBlock ) );
    if ( !hasFileBody ) return messages;

    return messages.map(( turn ) => {
        if ( !Array.isArray( turn?.content ) || !turn.content.some( isDropBlock ) ) return turn;
        return { ...turn, content: turn.content.filter(( block ) => !isDropBlock( block ) ) };
    });
}
// サーバーに保存されている履歴（最新のスナップショット）を画面側の履歴で全置換する。
// completionsはサーバーの保存内容を使って問い合わせるため、画面側とずれている場合に呼ぶ。
//   ・巻き戻し（会話の切り詰め）や履歴復元でずれたとき
//   ・messageで送れないターン（tool_result・添付ファイル付き）を渡すとき
// 直列化が必要なので、writeQueue()の中から呼ぶこと（保存はsaveHistory、問い合わせはsendが行う）。
// messages … 置き換える履歴（省略時は画面側の履歴すべて）
async syncHistory( signal, messages ) {
    const history = ( Array.isArray( messages ) )? messages: this.messages;
    await this.request(AiAssistantLlm.apiUrl.messages( this.conversationId ), 'PUT', {
        // 履歴は1レコード（1スナップショット）にまとめて保存する（空の場合はレコードなし）
        messages: ( history.length )? [{ contents: this.toApiHistory( history ) }]: []
    }, signal );
    // 画面側の履歴をそのまま置き換えたときだけ「同期済み」になる
    this.serverSynced = ( history === this.messages );
}
// 保存・問い合わせ用の履歴に整える。
// ・独自フィールド（_始まり）はそのまま渡す（プラットフォーム側でLLMへ渡す前に除去される）
// ・添付ファイルのメタ情報（_attachments）は、LLMが解析状態を判断できるようテキストブロックにする
toApiHistory( messages ) {
    const history = ( Array.isArray( messages ) )? messages: this.messages;
    return history.map(( message ) => {
        const turn = { ...message };
        const metaBlock = AiAssistantLlm.attachmentMetaBlock( message._attachments );
        if ( metaBlock && Array.isArray( turn.content ) ) {
            // tool_result（選択肢への回答など）は userターンのcontent先頭に置く必要があるため、
            // メタ情報テキストは tool_result ブロックの後ろに挿入する。
            const toolResults = turn.content.filter(( block ) => block && block.type === 'tool_result');
            const others = turn.content.filter(( block ) => !block || block.type !== 'tool_result');
            turn.content = [ ...toolResults, metaBlock, ...others ];
        }
        return turn;
    });
}
// 添付ファイルのメタ情報と、その取り扱い指示のテキストブロックを作る
static attachmentMetaBlock( attachments ) {
    if ( !Array.isArray( attachments ) || !attachments.length ) return null;

    const metaText = attachments.map(( file ) => {
        // 解析状態を判定してLLMに伝える
        //   未対応形式          … ネイティブに中身を読み取れない
        //   対応形式かつ解析オフ … ユーザーが「AIで解析」をオフにしている
        //   対応形式かつ解析オン … 中身（実体）も渡されている
        let analysisState;
        if ( !file.supported ) {
            analysisState = '未対応（この形式はAIが中身を直接解析できません）';
        } else if ( !file.use_llm ) {
            analysisState = '解析オフ（対応形式ですが、ユーザが「AIで解析」をオフにしているため中身は渡されていません）';
        } else {
            analysisState = '解析オン（ファイルの中身が渡されています）';
        }
        return `file_idが${file.file_id ?? ''}、ファイル名が${file.filename ?? ''}、MIMEタイプが${file.mime_type ?? ''}、ファイルサイズが${file.size ?? ''}、解析状態が「${analysisState}」`;
    }).join('\n');

    return {
        'type': 'text',
        'text': `添付ファイルの情報は以下の通りです。\n${metaText}\n\n`
            + `【添付ファイルの取り扱い指示】\n`
            + `・ユーザが添付ファイルの中身に関する質問（例：中身を調べて／要約して／内容を確認して 等）をしているのに、そのファイルの解析状態が「解析オフ」の場合は、ファイルの中身を推測で回答せず、「このファイルはAIで解析がオフになっています。ファイルの『AIで解析』をオンにして再度送信してください」と回答してください。\n`
            + `・解析状態が「未対応」のファイルについて中身を問われた場合は、「このファイル形式（MIMEタイプ）はAIが中身を直接解析できません」とその旨を回答してください。\n`
            + `・解析状態が「解析オン」のファイルは、渡された中身をもとに回答してください。`
    };
}
/*
##################################################
   AI応答の生成
##################################################
*/
// messageText … ユーザー発言（テキスト）。指定するとプラットフォーム側がユーザーターンを履歴へ追加し、
//                AI応答も含めて保存する（レスポンスの saved が true になる）。
//                nullのときはmessageを指定せず、同期済みの履歴（添付ファイルやtool_resultを含む
//                contentブロック）だけで問い合わせる（プラットフォーム側でユーザーターンを追加させない）。
async requestCompletion( signal, messageText = null ) {
    const body = {
        // 会話のデフォルトモデルを上書きする（フッターで切り替えたモデルを使う）
        model_id: this.modelId
    };
    if ( messageText !== null ) body.message = messageText;
    return await this.request(AiAssistantLlm.apiUrl.completion( this.conversationId ), 'POST', body, signal );
}
/*
##################################################
   応答のcontentブロック
##################################################
*/
// 画面側（AiAssistantChat）はcontentブロックの配列（text / tool_use / thinking）を処理する。
// 現在のプラットフォームAPIはテキスト部分（content）とstop_reasonのみを返すため、
// ブロック配列が返る場合はそれを優先し、返らない場合はテキストのみのブロックに組み立てる。
//
// 【制限事項】stop_reasonが"tool_use"の応答は、どのツールをどの引数で呼び出したか
// （tool_useブロック）がAPIの応答に含まれないため実行できない。ツール実行を伴う会話には
// completionsの応答にcontentブロックをそのまま返す拡張（content_blocks）が必要。
responseContents( data ) {
    if ( Array.isArray( data.content_blocks ) ) return data.content_blocks;
    if ( Array.isArray( data.content ) ) return data.content;

    if ( data.stop_reason === 'tool_use') {
        throw new Error('AIがツールの実行を要求しましたが、AIサービスの応答にツール呼び出しの内容（tool_useブロック）が含まれていないため実行できません。');
    }

    const text = ( typeof data.content === 'string')? data.content: '';
    return ( text )? [{ 'type': 'text', 'text': text }]: [];
}
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
   プラットフォームAPIへリクエストを送信する
##################################################
*/
async request( url, method, body, signal ) {
    const token = this.getToken();
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    if ( body ) options.body = JSON.stringify( body );
    if ( signal ) options.signal = signal;

    const response = await AiAssistantChat.fetchWithRetry( url, options, {
        retryStatuses: AiAssistantLlm.retryStatuses
    });

    const json = await response.json().catch( () => null );
    if ( !response.ok ) {
        // platform APIはエラー時も message を返すため、あればそれを利用する。
        // ステータスコードは呼び出し側での再送判断（タイムアウト確認）に使う。
        const error = new Error( json?.message ?? `AI Assistant request failed: ${response.status}`);
        error.status = response.status;
        throw error;
    }
    // 応答は { result, message, ts, data } の形なので data のみを返す
    return json?.data ?? {};
}

}
