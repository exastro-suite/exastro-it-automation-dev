////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / DevelopmentSupport.js
//
//   -----------------------------------------------------------------------------------------------
//
//   Copyright 2022 NEC Corporation
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

class DevelopmentSupport {
/*
##################################################
    Constructor
##################################################
*/
constructor( target ) {
    this.target = target;
}
/*
##################################################
    Setup
##################################################
*/
setup(llmSelect, apiParam) {
    return new Promise( async ( resolve, reject ) => {
        // Message
        this.message = [];

        // ファイル
        this.file = [];

        // 作業状態
        this.operation = false;

        // jQuery Object
        this.$ = {
            target: $( this.target )
        };

        // markdown-it
        this.md = markdownit({
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

        // LLM module
        try {
            this.model = llmSelect;
            this.v = fn.getUiVersion();
            const module  = await import(`/_/ita/js/development_support_module/${this.model}.js?v=${this.v}`);
            this.llm = new module.DevelopmentSupportModule();
            await this.llm.setup(apiParam);
        } catch ( error ) {
            console.error( error );
            reject( error );
        }

        // Main HTML
        this.$.target.html( this.mainHtml() );
        this.$.chat = this.$.target.find('.developmentSupportChatBlock');
        this.$.input = this.$.target.find('.developmentSupportInput');
        this.$.file = this.$.target.find('.developmentSupportInputFile');
        this.$.fileList = this.$.target.find('.developmentSupportFileList');
        this.$.send = this.$.target.find('.developmentSupportInputSubmit');

        // Textarea高さ調整
        this.$.target.find('.textareaAdjustmentWrap').css('height', '32px');

        // イベントセット
        this.setEvents();

        resolve();
    });
}
/*
##################################################
   作業開始
##################################################
*/
operationStart() {
    if ( this.operation ) return;
    this.operation = true;
}
/*
##################################################
   作業終了
##################################################
*/
operationEnd() {
    if ( !this.operation ) return;
    this.operation = false;
}
/*
##################################################
    Main HTML
##################################################
*/
mainHtml() {
    return ``
    + `<div class="developmentSupportContainer">`
        + `<div class="developmentSupportChatBlock">`
            + this.initialMessageHtml()
        + `</div>`
        + `<div class="developmentSupportFileBlock">`
            + `<ul class="developmentSupportFileList"></ul>`
        + `</div>`
        + `<div class="developmentSupportInputBlock">`
            + `<div class="developmentSupportInputTextBlock">`
                + fn.html.textarea('developmentSupportInput', '', 'developmentSupportInput', {'placeholder': 'Enterでメッセージを送信します。Shift+Enterで改行できます。'}, true )
            + `</div>`
            + `<div class="developmentSupportInputFileBlock">`
                + fn.html.button( fn.html.icon('plus'), 'developmentSupportInputFile itaButton button', { action: 'positive'})
            + `</div>`
            + `<div class="developmentSupportInputSubmitBlock">`
                + fn.html.button( fn.html.icon('upload'), 'developmentSupportInputSubmit itaButton button', { action: 'positive'})
            + `</div>`
        + `</div>`
    + `</div>`;
}
/*
##################################################
    初期メッセージ
##################################################
*/
initialMessageHtml() {
    return ``
    + `<div class="developmentSupportInitialMessage">`
        + `ご用件をお伺いしてもよろしいでしょうか？`
    + `</div>`;
}
/*
##################################################
    チャット HTML
##################################################
*/
updateChat( message ) {
    if ( this.message.length === 0 && message.role === 'user') {
        this.$.chat.html(`<ul class="developmentSupportList"></ul>`);
        this.$.chatList = this.$.chat.find('.developmentSupportList');
    }

    try {
        const $message = $(``
        + `<li class="developmentSupportItem" data-role="${message.role}">`
            + `${( message.role === 'support')? `<div class="developmentSupportItemIcon"></div>`: ``}`
            + `<div class="developmentSupportItemInner">`
            + `</div>`
        + `</li>`);
        if ( message.role === 'user') {
            $message.find('.developmentSupportItemInner').text( message.text );
        } else if ( message.role === 'support') {
            $message.find('.developmentSupportItemInner').html( this.loadingHtml() );
        }
        this.$.chatList.append( $message );
        setTimeout( () => {
            this.scrollChatArea( $message );
        }, 300 );
        return $message;
    } catch ( error ) {
        console.error( error );
    }
}
/*
##################################################
    チャットスクロール
##################################################
*/
scrollChatArea( $obj ) {
    const scrollTop = this.$.chat.scrollTop() + $obj.position().top - 16;
    this.$.chat.animate({ scrollTop: scrollTop }, 100 );
}
/*
##################################################
    ローディングHTML
##################################################
*/
loadingHtml() {
    return ``
    + `<div class="developmentSupportItemNowLoading">`
        + `<div class="developmentSupportItemNowLoading-dot developmentSupportItemNowLoading-dot-1"></div>`
        + `<div class="developmentSupportItemNowLoading-dot developmentSupportItemNowLoading-dot-2"></div>`
        + `<div class="developmentSupportItemNowLoading-dot developmentSupportItemNowLoading-dot-3"></div>`
        + `<div class="developmentSupportItemNowLoading-dot developmentSupportItemNowLoading-dot-4"></div>`
        + `<div class="developmentSupportItemNowLoading-dot developmentSupportItemNowLoading-dot-5"></div>`
    + `</div>`;
}
/*
##################################################
    イベント
##################################################
*/
setEvents() {
    this.setSendMessageEvent();
};
/*
##################################################
    メッセージ送信イベント
##################################################
*/
setSendMessageEvent() {
    // エンター
    this.$.input.on('keydown', async ( e ) => {
        if ( this.operation ) return;
        if ( e.key === 'Enter' && !e.shiftKey ) {
            this.$.send.prop('disabled', true );
            e.preventDefault();
            await this.sendMessage();
            this.$.send.prop('disabled', false );
        }
    });

    // 送信ボタン
    this.$.send.on('click', async ( e ) => {
        if ( this.operation ) return;
        this.$.send.prop('disabled', true );
        await this.sendMessage();
        this.$.send.prop('disabled', false );
    });
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
    ファイル準備
##################################################
*/
setFile( file ) {

}
/*
##################################################
    ファイルリストHTML
##################################################
*/
fileListHtml() {

}
/*
##################################################
    メッセージ送信
##################################################
*/
sendMessage( e ) {
    return new Promise( async ( resolve ) => {
        this.operationStart();

        // ユーザメッセージ
        const message = this.$.input.val();
        if ( message === '') return;
        this.$.input.val('').trigger('input');
        const userMessage = {
            role: 'user',
            text: message
        };
        const $userMessage = this.updateChat( userMessage );

        await this.sleep( 1000 );

        // サポートメッセージ
        const supportMessage = {
            role: 'support'
        };
        const $supportMessage = this.updateChat( supportMessage );
        try {
            const result = await this.llm.send( message );
            supportMessage.text = result;

            await this.sleep( 100 );

            $supportMessage.find('.developmentSupportItemInner').html( this.md.render( supportMessage.text ) );
            this.scrollChatArea( $supportMessage );

            this.message.push( userMessage );
            this.message.push( supportMessage );
        } catch ( error ) {
            if ( error && error.message && error.message.indexOf('Failed to fetch') === -1 ) {
                    alert( error.message );
            }

            // エラーが起きた場合はメッセージを削除し、入力欄にテキストを戻す
            $userMessage.remove();
            $supportMessage.remove();
            this.$.input.val( message ).trigger('input');
        }
        this.operationEnd();

        resolve();
    });
}

}