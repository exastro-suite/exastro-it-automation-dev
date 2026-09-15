////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / ai_assistant.js
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
class AiAssistant {
/*
##################################################
   Constructor
##################################################
*/
constructor( info, params ) {
    this.info = info;
    this.params = params;
    // 会話履歴タブの会話一覧（タブを開いたときに作る）
    this.conversationTable = null;
    // 会話履歴タブのボタンの処理中（同時に押されるのを防ぐ）
    this.conversationBusy = false;
}
/*
##################################################
   Setup
##################################################
*/
async setup() {
    const select = ( id ) => document.querySelector(`#${id} > .sectionBody`);
    this.el = {
        chat: select('ai_assistant_container'),
        conversations: select('ai_assistant_conversations'),
        lessons: select('ai_assistant_lessons')
    };
    await Promise.all([
        this.setupChat(),
        this.setupConversations(),
        this.setupLessons()
    ]);

    return;
}
// チャットタブ
async setupChat() {
    this.chat = new AiAssistantChat( this.params, {});
    await this.chat.mount(this.el.chat);
}
// 会話履歴タブ。保存されている会話の一覧（GET /conversations）を表示し、行のボタンから
// 会話の再開（チャットへの復元）と、保存されている会話履歴のJSON表示を行う。
// 一覧の取得はタブを最初に開いたときに行う（開かない場合はAPIを呼ばない）。
async setupConversations() {
    const aa = this;
    if ( !aa.el.conversations ) return;

    $('.contentMenuLink[href="#ai_assistant_conversations"]').on('click', function(){
        if ( aa.conversationTable ) return;

        aa.conversationTable = DataTablePF.conversationList('AAC', {
            promptProfile: AiAssistantLlm.promptProfile,
            // 会話に対する操作
            rowMenu: [
                { type: 'resume', icon: 'square_next', text: getMessage.FTE14033, action: 'positive'},
                { type: 'check', icon: 'detail', text: getMessage.FTE10059, action: 'default'}
            ],
            rowMenuAction: ( type, item ) => aa.conversationMenuAction( type, item ),
            // 選択した会話の削除（一番左にチェックボックスの列、メニューに削除ボタンが追加される）
            deleteAction: ( items ) => aa.deleteConversations( items )
        });
        // Tableのsetupで一覧の取得が始まる
        $( aa.el.conversations ).html( aa.conversationTable.setup() );
    });
}
conversationMenuAction( type, conversation ) {
    switch ( type ) {
        case 'resume':
            this.resumeConversation( conversation );
        break;
        case 'check':
            this.checkConversation( conversation );
        break;
    }
}
/*
##################################################
   会話の再開
##################################################
*/
// 保存されている会話履歴をチャット画面へ復元し、その会話の続きを話せるようにする。
async resumeConversation( conversation ) {
    const aa = this,
          chat = aa.chat,
          conversationId = conversation?.conversation_id;
    if ( !conversationId || !chat || aa.conversationBusy ) return;

    // 応答中に会話を差し替えると、進行中のツール実行の結果が復元した会話へ混ざってしまう
    if ( chat.isRunning ) {
        alert( getMessage.FTE14035 );
        return;
    }

    // 復元が終わるまで行のボタンを押せないようにする（一覧の表示はそのまま）
    aa.conversationBusy = true;
    aa.conversationTable.rowMenuDisabled();
    try {
        // チャット中の場合は、ここまでの内容を保存してから差し替える
        if ( chat.newChat !== true ) {
            // 表示用の情報（発言時刻・表示文言など）を含む最新の履歴を保存しておく。
            // 失敗しても再開は妨げない（保存は応答完了時にも行われている）。
            try {
                await chat.historyEnqueue();
            } catch ( error ) {
                console.warn('会話を再開する前の履歴保存に失敗しました。', error );
            }
        }

        const history = await AiAssistantLlm.fetchHistory( conversationId );
        if ( fn.typeof( history ) !== 'array' || !history.length ) {
            alert( getMessage.FTE14036 );
            return;
        }
        // 新規チャット相当の初期化（入力欄の構築・LLMの用意）を行ってから履歴を復元する
        // （初期化を飛ばすと入力欄が無くなる）。自動再開と同じ順序。
        await chat.newChatStart();
        await chat.resumeChat( history, conversationId );

        // 復元したチャットを表示する（タブをクリックしたときと同じ切り替え）
        $('.contentMenuLink[href="#ai_assistant_container"]').trigger('click');
    } catch ( error ) {
        console.error( error );
        alert( getMessage.FTE14037 + '\n' + fn.cv( error?.message, ''));
    } finally {
        aa.conversationBusy = false;
        aa.conversationTable.rowMenuDisabled( false );
    }
}
/*
##################################################
   会話履歴の確認
##################################################
*/
// 保存されている会話履歴（LLMへ渡すターンの配列）をJSONとしてエディターで表示する。
async checkConversation( conversation ) {
    const aa = this,
          conversationId = conversation?.conversation_id;
    if ( !conversationId || aa.conversationBusy ) return;

    // 取得が終わるまで行のボタンを押せないようにする（一覧の表示はそのまま）
    aa.conversationBusy = true;
    aa.conversationTable.rowMenuDisabled();

    let history;
    try {
        history = await AiAssistantLlm.fetchHistory( conversationId );
    } catch ( error ) {
        console.error( error );
        alert( getMessage.FTE14038 + '\n' + fn.cv( error?.message, ''));
        return;
    } finally {
        aa.conversationBusy = false;
        aa.conversationTable.rowMenuDisabled( false );
    }

    // fn.fileEditorはファイルの内容を表示する（拡張子.jsonでJSONとして色分けされる）
    const fileName = `${conversationId}.json`,
          file = new File([ JSON.stringify( history, null, 4 ) ], fileName, { type: 'application/json'});
    await fn.fileEditor( file, fileName, 'preview', {});
}
/*
##################################################
   会話履歴の削除
##################################################
*/
// 一覧で選択した会話の履歴を削除する。確認をとってから1件ずつ削除し、
// 削除できなかったものがあればまとめて知らせる。
// 戻り値がfalseのときは一覧を取得しなおさない（確認をキャンセルした場合）。
async deleteConversations( conversations ) {
    const aa = this,
          chat = aa.chat;
    if ( aa.conversationBusy || fn.typeof( conversations ) !== 'array' || !conversations.length ) return false;

    const title = getMessage.FTE14039;

    // 応答中の会話を削除しても、応答の完了時に履歴が保存されなおしてしまう
    const currentId = chat?.llm?.conversationId;
    if ( chat?.isRunning && conversations.some(( item ) => item.conversation_id === currentId ) ) {
        await fn.alert( title, getMessage.FTE14040 );
        return false;
    }

    const check = await fn.iconConfirm('circle_exclamation', title,
        getMessage.FTE14041( conversations.length ) );
    if ( !check ) return false;

    aa.conversationBusy = true;
    const processing = fn.processingModal( title );

    const errors = [],
          deletedIds = [];
    for ( const conversation of conversations ) {
        const conversationId = conversation?.conversation_id;
        if ( !conversationId ) continue;
        try {
            await AiAssistantLlm.deleteHistory( conversationId );
            deletedIds.push( conversationId );
        } catch ( error ) {
            console.error( error );
            errors.push(`${fn.cv( conversation.title, conversationId )}：${fn.cv( error?.message, '')}`);
        }
    }

    // 表示中のチャットの会話を削除した場合は、そのまま続けると履歴が保存されなおすため
    // 新しいチャットへ戻す（保存はしない）
    if ( chat && currentId && deletedIds.indexOf( currentId ) !== -1 ) {
        await chat.newChatStart();
    }

    processing.close();
    aa.conversationBusy = false;

    if ( errors.length ) {
        await fn.alert( title, getMessage.FTE14042( errors.length ) + '<br>'
            + fn.escape( errors.join('\n'), true ) );
    }
    return;
}
async setupLessons() {

}

}