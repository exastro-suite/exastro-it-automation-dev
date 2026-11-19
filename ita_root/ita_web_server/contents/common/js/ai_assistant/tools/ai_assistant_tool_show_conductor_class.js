////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / ai_assistant_tool_show_conductor_class.js
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

// 画面専用ツール「show_conductor_class」（Conductor構成の表示）。
//
// ・MCPサーバーではなく画面側（このクラス）で実行するツール。ツール定義（LLMへ渡す内容）と
//   その動作を1ファイルにまとめている。
// ・conductor_class_id を受け取り、チャット欄にConductorの構成（閲覧モード）を表示する。
// ・get-conductor-class は LLM が内容を読むだけのツールで、画面には何も表示しない。
//   ユーザーが構成を見たいときだけ、LLM がこのツールを呼ぶ。
// ・構成の取得・描画は画面側で行うため、構成の内容は LLM には返らない（表示した旨だけ返す）。
// ・履歴復元時も同じ吹き出しを再表示する。
class AiAssistantToolShowConductorClass {
/*
##################################################
   ツール定義
##################################################
*/
static get toolName() {
    return 'show_conductor_class';
}
// LLMへ渡すツール定義（MCPのtools/listと同じ形式。inputSchemaはLLM層でinput_schemaへ変換される）
static get definition() {
    return {
        name: AiAssistantToolShowConductorClass.toolName,
        description: 'conductor_class_id で指定したConductorの構成（ノードと線の図）を、ユーザーが見られるようにチャット欄へ表示するための画面専用ツール。'
            + 'ユーザーが「Conductorを見せて」「構成を確認したい」など、Conductorの内容を目で見たいと求めたときだけ使う。'
            + 'LLMが内容を把握するだけなら get-conductor-class を使うこと（get-conductor-class は画面に何も表示しない）。'
            + 'create-conductor・update-conductor は実行結果の構成を自動で表示するため、その直後にこのツールを呼ぶ必要はない。'
            + '同じConductorに対して繰り返し呼ばないこと。'
            + '注意: 構成の内容はLLMには返らない（表示した旨のみ返る）。',
        inputSchema: {
            type: 'object',
            properties: {
                conductor_class_id: {
                    type: 'string',
                    description: '表示するConductor Class ID。'
                }
            },
            required: [ 'conductor_class_id' ]
        }
    };
}
/*
##################################################
   Constructor
##################################################
*/
// chat … AiAssistantChat（吹き出しの生成・構成の描画はチャット側に委ねる）
constructor( chat ) {
    this.chat = chat;
}
/*
##################################################
   実行
##################################################
*/
// 構成の吹き出しを表示し、LLMには表示した旨だけを tool_result で返す。
async execute( toolUse ) {
    const classId = this.classId( toolUse );

    if ( !classId ) {
        return {
            type: 'tool_result',
            tool_use_id: toolUse.id ?? '',
            is_error: true,
            content: 'conductor_class_id is required'
        };
    }

    // 待機中（思考中）インジケータが残っていれば消してから表示する。
    this.chat.elements.chatList
        ?.querySelectorAll('.aiAssistantChatItemLoading')
        .forEach(( item ) => item.remove() );

    const el = this.chat.appendConductorClassPreview( classId );
    if ( el ) setTimeout(() => { this.chat.scrollChatArea( el ); }, 100 );

    return {
        type: 'tool_result',
        tool_use_id: toolUse.id ?? '',
        content: `Displayed the configuration of Conductor class ${classId} to the user.`
    };
}
/*
##################################################
   履歴からの復元
##################################################
*/
// 履歴復元時は、保存された入力（conductor_class_id）から構成を再表示する。
resume( toolUse ) {
    const classId = this.classId( toolUse );
    if ( !classId ) return;
    this.chat.appendConductorClassPreview( classId );
}
// ツール入力から conductor_class_id を取り出す。
classId( toolUse ) {
    const input = toolUse?.arguments ?? toolUse?.input ?? {};
    const id = input.conductor_class_id;
    return ( id === undefined || id === null )? '': String( id ).trim();
}
}
