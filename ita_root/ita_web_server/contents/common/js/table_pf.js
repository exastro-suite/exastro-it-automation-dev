////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / table_pf.js
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

// プラットフォームAPIの一覧を表示するTable。
//
// ・HTML構造・CSSクラス名は table.js（DataTable）に合わせているため、common.cssのTable用スタイルが
//   そのまま適用される。メニュー情報（menu_info / column_info）は使わず、カラム定義を渡して組み立てる。
// ・ページの切り替えは、その都度APIから該当ページ分だけを取得する（サーバーサイドページング）。
//   table.js のようにWorkerへ全件を渡して絞り込む方式は取らない。
// ・件数・最大ページ数はAPIが返す総件数から求めるため、総件数の取り出し方を params.total で渡す
//   （総件数を返すAPIのみ対応）。
//
// AIアシスタントの会話一覧（GET /conversations）はstaticメソッドでインスタンスを作れる。
//
//   const table = DataTablePF.conversationList('conversationTable');
//   $target.html( table.setup() );
//
// 任意の一覧を表示する場合はカラム定義とAPIを渡す。
//
//   const table = new DataTablePF('someTable', {
//       columns: [
//           { key: 'name', name: '名前', width: '240px'},
//           { key: 'date', name: '日時', type: 'datetime'}
//       ],
//       rest: ( limit, offset ) => `/api/.../items?limit=${limit}&offset=${offset}`,
//       list: ( data ) => data.items,
//       total: ( data ) => data.total_count
//   });
//
// カラム定義（columns）で指定できるもの
//   key       … 表示するデータのキー（cellを指定する場合は列の識別子としてのみ使われる）
//   name      … 見出しの文言
//   type      … 'text'（既定） / 'number'（右寄せ） / 'date' / 'datetime'
//   width     … 列の最大幅（CSSの値）
//   wrap      … trueで折り返して表示する（既定は1行で省略表示）
//   className … セルに追加するクラス名
//   cell      … セルのHTMLを返す関数 ( item, column ) => html（値は呼び出し側でエスケープする）
//
// option で指定できるもの
//   onePageNum    … 1ページに表示する件数（省略時は前回選択した件数）
//   rowMenu       … 行ごとのボタン [{ type, text, icon, action }]（先頭にボタン1つにつき1列を作る）
//   rowMenuAction … 行のボタンを押したときの処理 ( type, item ) => void
//   select        … trueで一番左にチェックボックスの列を追加する（deleteAction指定時は自動で追加）
//   deleteAction  … 選択した行の削除処理 ( items ) => Promise（メニューに削除ボタンを追加する）
//                   処理のあと一覧を取得しなおす。falseを返すと取得しなおさない（確認をキャンセルした場合など）
//   errorTitle    … 取得に失敗したときの見出し
class DataTablePF {
/*
##################################################
   1ページに表示する件数
##################################################
*/
static get onePageNumList() {
    return [ 10, 25, 50, 75, 100 ];
}
static get defaultOnePageNum() {
    return 25;
}
/*
##################################################
   再送するHTTPステータス（一過性のエラーのみ）
##################################################
*/
static get retryStatuses() {
    return [ 425, 429, 500, 502, 503 ];
}
/*
##################################################
   会話一覧のTable
##################################################
*/
// AIアシスタントの会話（T_CHAT_CONVERSATION）の一覧を表示するTableを作る。
// 会話に対する操作（再開など）は option.rowMenu / option.rowMenuAction で渡す。
static conversationList( tableId, option = {}) {
    const { organizationId, workspaceId } = fn.getCommonParams();
    const endPoint = `/api/${organizationId}/platform/workspaces/${workspaceId}/conversations`;

    // 会話一覧はprompt_profileでの絞り込みが必須。省略時はAIアシスタントが使うプロファイル。
    const promptProfile = fn.cv( option.promptProfile,
        ( typeof AiAssistantLlm !== 'undefined')? AiAssistantLlm.promptProfile: '');

    return new DataTablePF( tableId, {
        columns: DataTablePF.conversationColumns,
        rest: ( limit, offset ) => `${endPoint}?prompt_profile=${encodeURIComponent( promptProfile )}`
            + `&limit=${limit}&offset=${offset}`,
        list: ( data ) => ( Array.isArray( data?.conversations ) )? data.conversations: [],
        // total_countは絞り込み条件（prompt_profile・status）に合致する総件数（limit/offset適用前）。
        // countは取得したページの件数なので使わない。
        total: ( data ) => data?.total_count
    }, option );
}
/*
##################################################
   会話一覧のカラム定義
##################################################
*/
static get conversationColumns() {
    return [
        { key: 'title', name: getMessage.FTE14028, width: '480px', wrap: true},
        //{ key: 'status', name: getMessage.FTE14029, width: '100px'},
        //{ key: 'model_id', name: getMessage.FTE14025, width: '320px'},
        // message_countは最新のスナップショットに含まれる発言（ターン）の数
        { key: 'message_count', name: getMessage.FTE14030, type: 'number', width: '100px'},
        { key: 'current_token_count', name: getMessage.FTE14031, type: 'number', width: '120px'},
        { key: 'created_at', name: getMessage.FTE14026, type: 'datetime', width: '180px'},
        { key: 'updated_at', name: getMessage.FTE01017, type: 'datetime', width: '180px'},
        { key: 'conversation_id', name: getMessage.FTE14032, width: '240px'}
    ];
}
/*
##################################################
   行ごとのボタンの列
##################################################
*/
// option.rowMenu で渡されたボタンを1つずつ列に分けて作る（見出しはボタンの文言）。
// 押されたボタンの種別（type）は setTableEvents() が option.rowMenuAction へ渡す。
static rowMenuColumns( rowMenu ) {
    const columns = [];
    for ( const item of rowMenu ) {
        columns.push({
            key: `rowMenu_${item.type}`,
            name: item.text,
            className: 'tBodyTdButton',
            cell: () => fn.html.iconButton( item.icon, fn.cv( item.text, '', true ),
                ['itaButton', 'actionButton', 'pfTableRowMenuButton'],
                { type: item.type, action: fn.cv( item.action, 'default') })
        });
    }
    return columns;
}
/*
##################################################
   選択用の列
##################################################
*/
// 一番左に置くチェックボックスの列。見出しは一括選択ボタン、セルは行ごとのチェックボックスで、
// HTML・クラス名はtable.jsの選択列（.tHeadRowSelect / .tBodyRowSelect）に合わせている。
static get selectColumn() {
    return { key: 'pfTableSelect', select: true };
}
/*
##################################################
   Constructor
   params {
      columns: カラム定義の配列
      rest: ( limit, offset ) => 一覧取得のURL
      list: ( data ) => 一覧の配列（省略時は応答をそのまま配列として扱う）
      total: ( data ) => 総件数
   }
   option {
      onePageNum: 1ページに表示する件数（省略時は前回選択した件数）
      rowMenu: 行ごとに並べるボタン [{ type, text, icon, action }]
      rowMenuAction: ( type, item ) => void（行のボタンを押したときの処理）
      select: trueで選択用のチェックボックスの列を追加する
      deleteAction: ( items ) => Promise（選択した行の削除処理）
      errorTitle: 取得に失敗したときの見出し
   }
##################################################
*/
constructor( tableId, params, option = {}) {
    const tb = this;
    tb.id = tableId;
    tb.params = params;
    tb.option = option;

    // 削除するには行を選択する必要があるため、削除処理があれば選択できるようにする
    tb.selectFlag = ( option.select === true || fn.typeof( option.deleteAction ) === 'function');

    tb.columns = ( fn.typeof( params.columns ) === 'array')? params.columns: [];

    // 行ごとのボタンは先頭の列に表示する（ボタン1つにつき1列）
    if ( fn.typeof( option.rowMenu ) === 'array' && option.rowMenu.length ) {
        tb.columns = DataTablePF.rowMenuColumns( option.rowMenu ).concat( tb.columns );
    }

    // 選択用のチェックボックスは一番左の列
    if ( tb.selectFlag ) {
        tb.columns = [ DataTablePF.selectColumn ].concat( tb.columns );
    }

    // テーブルデータ
    tb.data = {
        body: null
    };

    // ページング
    tb.paging = {
        pageNum: 1, // 表示するページ
        pageMaxNum: 1, // 最大ページ数
        num: 0, // 件数
        onePageNum: DataTablePF.defaultOnePageNum
    };

    // 1頁に表示する数（table.jsと同じ設定を引き継ぐ）
    if ( option.onePageNum ) {
        tb.paging.onePageNum = Number( option.onePageNum );
    } else {
        const onePageNum = fn.storage.get('onePageNum', 'local', false );
        if ( onePageNum ) tb.paging.onePageNum = Number( onePageNum );
    }

    // 待機中
    tb.workType = '';
    tb.workTimer = null;
    // 削除の処理中（確認中も含む。処理が終わるまで削除ボタンを押せないようにする）
    tb.deleteBusy = false;
}
/*
##################################################
    Work check
    > 非同期イベントの状態
##################################################
*/
workStart( type, time = 50 ) {
    const tb = this;
    if ( tb.workType ) return;

    // 読み込み中になったら
    tb.$.window.trigger( tb.id + '__tableStandBy');

    tb.workType = type;

    const standBy = function() {
        tb.$.container.removeClass('noData');
        tb.$.message.empty();
        tb.$.container.addClass(`standBy ${tb.workType}StandBy`);
    };

    if ( time > 0 ) {
        // 画面上の待機状態タイミングを遅らせる
        tb.workTimer = setTimeout( function() {
            standBy();
        }, time );
    } else {
        standBy();
    }
}
workEnd() {
    const tb = this;
    if ( tb.workTimer ) clearTimeout( tb.workTimer );
    tb.$.container.removeClass(`standBy ${tb.workType}StandBy`);

    // 完了したら
    tb.$.window.trigger( tb.id + '__tableReady');

    tb.workType = '';
}
get checkWork() {
    return ( this.workType !== '');
}
/*
##################################################
    Main HTML
##################################################
*/
mainHtml() {
    const tb = this;

    return ``
    + `<div id="${tb.id}" class="tableContainer viewTable standardTable pfTable">`
        + `<div class="tableHeader"></div>`
        + `<div class="tableBody tableVertical">`
            + `<div class="tableWrap">`
                + `<div class="tableBorder">`
                    + `<table class="table mainTable">`
                        + `<thead class="thead">${tb.theadHtml()}</thead>`
                        + `<tbody class="tbody"></tbody>`
                    + `</table>`
                + `</div>`
            + `</div>`
            + `<div class="tableMessage"></div>`
        + `</div>`
        + `<div class="tableFooter">${tb.footerHtml()}</div>`
        + `<div class="tableErrorMessage"></div>`
        + `<div class="tableLoading"></div>`
        + `<style class="tableStyle">${tb.styleHtml()}</style>`
    + `</div>`;
}
/*
##################################################
    Setup
    > $containerを返すので、呼び出し側で画面へ追加する
##################################################
*/
setup() {
    const tb = this;

    // jQueryオブジェクトキャッシュ
    tb.$ = {};
    tb.$.window = $( window );
    tb.$.container = $( tb.mainHtml() );
    tb.$.header = tb.$.container.find('.tableHeader');
    tb.$.body = tb.$.container.find('.tableBody');
    tb.$.wrap = tb.$.container.find('.tableWrap');
    tb.$.table = tb.$.container.find('.table');
    tb.$.thead = tb.$.container.find('.thead');
    tb.$.tbody = tb.$.container.find('.tbody');
    tb.$.footer = tb.$.container.find('.tableFooter');
    tb.$.message = tb.$.container.find('.tableMessage');
    tb.$.errorMessage = tb.$.container.find('.tableErrorMessage');
    tb.$.style = tb.$.container.find('.tableStyle');

    // Table headerメニュー（再読込・削除）
    const menuMainList = [
        { button: { icon: 'update01', text: getMessage.FTE01047, type: 'tableReload', action: 'default', minWidth: '160px'}}
    ];
    const menuSubList = [];
    // 削除ボタンは行が選択されるまで押せない（updateSelectStatusで切り替える）
    if ( fn.typeof( tb.option.deleteAction ) === 'function') {
        menuMainList.push({ button: { icon: 'trash', text: getMessage.FTE00188, type: 'tableDelete',
            action: 'danger', disabled: true, minWidth: '160px' }});
    }
    tb.$.header.html( fn.html.operationMenu({ Main: menuMainList, Sub: menuSubList }));

    tb.$.header.find('.itaButton[data-type="tableReload"]').on('click', function(){
        if ( !tb.checkWork ) tb.reload();
    });
    tb.setDeleteEvent();

    tb.setPagingEvent();
    tb.setTableEvents();
    tb.updateFooterStatus();

    tb.workStart('table', 0 );
    tb.requestBody();

    return tb.$.container;
}
/*
##################################################
    Table内各種イベント
##################################################
*/
setTableEvents() {
    const tb = this;

    // 行の選択（チェックボックス）
    if ( tb.selectFlag ) tb.setSelectEvent();

    // 行ごとのボタン（rowMenuActionが指定された場合のみ）
    if ( fn.typeof( tb.option.rowMenuAction ) !== 'function') return;

    tb.$.tbody.on('click', '.pfTableRowMenuButton', function(){
        if ( tb.checkWork ) return;

        const $button = $( this ),
              index = Number( $button.closest('.tBodyTr').attr('data-index') ),
              item = tb.data.body?.[ index ];
        if ( item !== undefined ) tb.option.rowMenuAction( $button.attr('data-type'), item );
    });
}
/*
##################################################
    行の選択
##################################################
*/
setSelectEvent() {
    const tb = this;

    // 見出しの一括選択（ボタンの外側がクリックされた場合もボタンを押したことにする）
    tb.$.thead.on('click', '.tHeadRowSelect', function( e ){
        if ( tb.checkWork ) return;
        if ( !$( e.target ).closest('.rowSelectButton').length ) {
            $( this ).find('.rowSelectButton').focus().click();
        }
    });
    tb.$.thead.on('click', '.rowSelectButton', function(){
        if ( tb.checkWork ) return;

        // 選択されていないときは全選択、それ以外（一部・すべて選択）は選択を解除する
        const checked = ( $( this ).attr('data-select') === 'not');
        tb.$.tbody.find('.pfTableRowCheck').prop('checked', checked );
        tb.updateSelectStatus();
    });

    // セルのどこをクリックしてもチェックを切り替える
    tb.$.tbody.on('click', '.tBodyRowSelect', function( e ){
        if ( tb.checkWork ) return;
        if ( !$( e.target ).closest('.checkboxWrap').length ) {
            const $check = $( this ).find('.pfTableRowCheck');
            $check.focus().prop('checked', !$check.prop('checked') ).change();
        }
    });
    tb.$.tbody.on('change', '.pfTableRowCheck', function(){
        tb.updateSelectStatus();
    });
}
// 一括選択ボタンの見た目と、選択した行に対するボタン（削除）の活性状態を更新する
updateSelectStatus() {
    const tb = this;
    if ( !tb.selectFlag ) return;

    const length = tb.$.tbody.find('.pfTableRowCheck').length,
          checkedLength = tb.$.tbody.find('.pfTableRowCheck:checked').length;

    tb.$.thead.find('.rowSelectButton').attr('data-select',
        ( length && length === checkedLength )? 'all': ( checkedLength )? 'oneOrMore': 'not');

    // 行を1つでも選択している場合のみ削除できる（削除の処理中は押せない）
    tb.$.header.find('.itaButton[data-type="tableDelete"]')
        .prop('disabled', ( tb.deleteBusy || checkedLength === 0 ) );
}
// 選択されている行のデータ（表示しているページ内のみ）
get selectedItems() {
    const tb = this;

    const items = [];
    tb.$.tbody.find('.pfTableRowCheck:checked').each(function(){
        const item = tb.data.body?.[ Number( $( this ).val() ) ];
        if ( item !== undefined ) items.push( item );
    });
    return items;
}
/*
##################################################
    削除
##################################################
*/
// 削除そのものは option.deleteAction（確認・API呼び出し）に任せ、
// 処理の前後のボタン制御と、削除した行を消すための取得しなおしを行う。
setDeleteEvent() {
    const tb = this;

    if ( fn.typeof( tb.option.deleteAction ) !== 'function') return;

    tb.$.header.on('click', '.itaButton[data-type="tableDelete"]', async function(){
        if ( tb.checkWork || tb.deleteBusy ) return;

        const items = tb.selectedItems;
        if ( !items.length ) return;

        // 削除の間は続けて押されないようにする（Tableは待機状態にせず一覧は表示したままにする）
        tb.deleteBusy = true;
        tb.updateSelectStatus();
        tb.rowMenuDisabled();

        let result;
        try {
            result = await tb.option.deleteAction( items );
        } catch ( error ) {
            console.error( error );
            result = false;
        }
        tb.deleteBusy = false;
        tb.rowMenuDisabled( false );

        // 削除した行が消えるように取得しなおす（キャンセルされた場合は選択したままにする）
        if ( result !== false ) {
            tb.reload();
        } else {
            tb.updateSelectStatus();
        }
    });
}
// 行のボタンをまとめて使用不可にする。ボタンを押したあとの処理中に、続けて押されるのを
// 防ぐために使う（Tableを待機状態にすると一覧が見えなくなるため、ボタンだけを止める）。
rowMenuDisabled( disabled = true ) {
    this.$.tbody.find('.pfTableRowMenuButton').prop('disabled', !!disabled );
}
/*
##################################################
    Style（カラム幅）
##################################################
*/
styleHtml() {
    const tb = this;

    const style = [];
    for ( const column of tb.columns ) {
        if ( !column.width ) continue;
        style.push(`#${tb.id} .tbody .ci[data-key="${column.key}"]{max-width:${column.width}}`);
    }
    return style.join('');
}
/*
##################################################
    tHead HTML
##################################################
*/
theadHtml() {
    const tb = this;

    const html = [];
    for ( const column of tb.columns ) {
        // 選択用の列の見出しは一括選択ボタン
        if ( column.select ) {
            html.push( fn.html.cell( fn.html.button('', 'rowSelectButton', { select: 'not'}),
                ['tHeadTh', 'tHeadLeftSticky', 'tHeadRowSelect'], 'th'));
            continue;
        }

        const className = ['tHeadTh'];
        if ( column.type === 'number') className.push('tBodyTdNumber');

        const name = fn.cv( column.name, '', true );
        html.push( fn.html.cell( name, className, 'th', 1, 1, { key: column.key }));
    }
    return fn.html.row( html.join(''), ['tHeadTr', 'headerTr']);
}
/*
##################################################
    tBody HTML
##################################################
*/
tbodyHtml() {
    const tb = this,
          list = tb.data.body;

    const html = [];
    for ( let i = 0; i < list.length; i++ ) {
        const rowHtml = [];
        for ( const column of tb.columns ) {
            rowHtml.push( tb.cellHtml( list[i], column, i ) );
        }
        // 行のボタン（rowMenu）から元データを引けるよう、行番号を持たせる
        html.push(`<tr class="tBodyTr tr" data-index="${i}">${rowHtml.join('')}</tr>`);
    }
    return html.join('');
}
/*
##################################################
    Cell HTML
##################################################
*/
cellHtml( item, column, index ) {
    const tb = this;

    // 選択用の列はチェックボックス（値は行番号。選択した行のデータは selectedItems で引く）
    if ( column.select ) {
        const name = `${tb.id}__ROWCHECK`,
              checkbox = fn.html.check('pfTableRowCheck', index, name, `${name}__${index}`);
        return fn.html.cell( checkbox, ['tBodyLeftSticky', 'tBodyRowSelect', 'tBodyTh'], 'th');
    }

    const className = ['tBodyTd'];
    if ( column.type === 'number') className.push('tBodyTdNumber');
    if ( column.className ) className.push( column.className );

    // セルの中身（.ci）はカラム幅のstyleで参照するためkeyを持たせる
    const ciClassName = ['ci'];
    if ( column.wrap ) ciClassName.push('textOverWrap');

    let value;
    if ( fn.typeof( column.cell ) === 'function') {
        // 独自描画（エスケープはカラム定義側の責任）
        value = column.cell( item, column );
    } else {
        value = tb.cellValue( item[ column.key ], column );
    }

    return ``
    + `<td class="${className.join(' ')} td" data-key="${fn.escape( column.key )}">`
        + `<div class="${ciClassName.join(' ')}" data-key="${fn.escape( column.key )}">${value}</div>`
    + `</td>`;
}
// 値をカラムの型に合わせた表示文字列（エスケープ済み）へ変換する
cellValue( value, column ) {
    switch ( column.type ) {
        case 'date':
            return fn.escape( fn.date( fn.cv( value, ''), 'yyyy/MM/dd') );
        case 'datetime':
            return fn.escape( fn.date( fn.cv( value, ''), 'yyyy/MM/dd HH:mm:ss') );
        case 'number': {
            const number = Number( value );
            return ( value === null || value === undefined || value === '' || Number.isNaN( number ) )
                ? '': String( number.toLocaleString() );
        }
        default:
            return fn.cv( value, '', true );
    }
}
/*
##################################################
    Footer HTML
##################################################
*/
footerHtml() {
    const tb = this;

    const onePageNumOptions = [];
    for ( const item of DataTablePF.onePageNumList ) {
        const id = `${tb.id}_pagingOnePageNumSelectRadio_${item}`,
              name = `${tb.id}_pagingOnePageNumSelectRadio`;
        onePageNumOptions.push(`<li class="pagingOnePageNumSelectItem">`
        + `<input class="pagingOnePageNumSelectRadio" type="radio" id="${id}" name="${name}" value="${item}">`
        + `<label class="pagingOnePageNumSelectLabel" for="${id}">${item}</label></li>`);
    }

    return `
    <div class="tableFooterInner">
        <div class="tableFooterBlock pagingAllNum">
            <dl class="tableFooterList">
                <dt class="tableFooterTitle"><span class="footerText pagingAllTitle">` + getMessage.FTE10029 + `</span></dt>
                <dd class="tableFooterItem tableFooterData"><span class="footerText pagingAllNumNumber">` + getMessage.FTE00059 + `</span></dd>
            </dl>
        </div>
        <div class="tableFooterBlock pagingOnePageNum">
            <dl class="tableFooterList">
                <dt class="tableFooterTitle"><span class="footerText">` + getMessage.FTE00060 + `</span></dt>
                <dd class="tableFooterItem tableFooterData">
                    <div class="pagingOnePageNumSelect">
                        <div class="pagingOnePageNumSelectNumber"></div>
                        <ul class="pagingOnePageNumSelectList">
                            ${onePageNumOptions.join('')}
                        </ul>
                    </div>
                </dd>
            </dl>
        </div>
        <div class="tableFooterBlock pagingMove">
            <ul class="tableFooterList">
                <li class="tableFooterItem">
                    <button class="pagingMoveButton" data-type="first" disabled>${fn.html.icon('first')}</button>
                </li>
                <li class="tableFooterItem">
                    <button class="pagingMoveButton" data-type="prev" disabled>${fn.html.icon('prev')}</button>
                </li>
                <li class="tableFooterItem">
                    <div class="pagingPage">
                        <span class="pagingCurrentPage">0</span>
                        <span class="pagingSeparate">/</span>
                        <span class="pagingMaxPageNumber">0</span>
                        <span class="pagingPageJumpNumber">` + getMessage.FTE00061 + `</span>
                    </div>
                </li>
                <li class="tableFooterItem">
                    <button class="pagingMoveButton" data-type="next" disabled>${fn.html.icon('next')}</button>
                </li>
                <li class="tableFooterItem">
                    <button class="pagingMoveButton" data-type="last" disabled>${fn.html.icon('last')}</button>
                </li>
            </ul>
        </div>
    </div>`;
}
/*
##################################################
   Update footer status
   > Table情報を更新する
##################################################
*/
updateFooterStatus() {
    const tb = this;

    tb.$.footer.find('.pagingAllNumNumber')
        .text( tb.paging.num.toLocaleString() + getMessage.FTE00063 );
    tb.$.footer.find('.pagingOnePageNumSelectRadio').val([ tb.paging.onePageNum ]);
    tb.$.footer.find('.pagingOnePageNumSelectNumber').text( tb.paging.onePageNum );

    const $paging = tb.$.footer.find('.pagingMove');
    $paging.find('.pagingCurrentPage').text( tb.paging.pageNum );
    $paging.find('.pagingMaxPageNumber').text( tb.paging.pageMaxNum.toLocaleString() );

    const prevFlag = ( tb.paging.pageNum <= 1 );
    $paging.find('.pagingMoveButton[data-type="first"], .pagingMoveButton[data-type="prev"]')
        .prop('disabled', prevFlag );

    const nextFlag = ( tb.paging.pageMaxNum === tb.paging.pageNum );
    $paging.find('.pagingMoveButton[data-type="last"], .pagingMoveButton[data-type="next"]')
        .prop('disabled', nextFlag );
}
/*
##################################################
   Paging event
##################################################
*/
setPagingEvent() {
    const tb = this;

    const $list = tb.$.footer.find('.pagingOnePageNumSelectList');

    tb.$.footer.find('.pagingMoveButton').on('click', function(){
        if ( tb.checkWork ) return;

        const type = $( this ).attr('data-type');
        switch ( type ) {
            case 'first':
                tb.paging.pageNum = 1;
            break;
            case 'last':
                tb.paging.pageNum = tb.paging.pageMaxNum;
            break;
            case 'prev':
                tb.paging.pageNum -= 1;
            break;
            case 'next':
                tb.paging.pageNum += 1;
            break;
        }
        // ページの切り替えは、その都度APIから該当ページ分を取得する
        tb.workStart('table');
        tb.requestBody();
    });

    tb.$.footer.find('.pagingOnePageNumSelectRadio').on('change', function(){
        if ( tb.checkWork ) return;

        const selectNo = Number( $( this ).val() );
        tb.paging.onePageNum = selectNo;
        tb.$.footer.find('.pagingOnePageNumSelectNumber').text( selectNo );
        $list.removeClass('pagingOnePageOpen');
        fn.storage.set('onePageNum', selectNo, 'local', false );

        // 1ページの件数が変わるとページの区切りも変わるため、先頭ページから取得しなおす
        tb.paging.pageNum = 1;
        tb.workStart('table');
        tb.requestBody();
    });

    tb.$.footer.find('.pagingOnePageNumSelectNumber').on('click', function(){
        if ( tb.checkWork ) return;

        if ( !$list.is('.pagingOnePageOpen') ) {
            const height = tb.$.header.outerHeight() + tb.$.body.outerHeight();
            $list.addClass('pagingOnePageOpen').css('max-height', height );
            $( window ).on(`pointerdown.${tb.id}_pagingOnePageNum`, function(e){
                if ( !$( e.target ).closest('.pagingOnePageNumSelect').length ) {
                    $( this ).off(`pointerdown.${tb.id}_pagingOnePageNum`);
                    $list.removeClass('pagingOnePageOpen');
                }
            });
        } else {
            $list.removeClass('pagingOnePageOpen');
            $( window ).off(`pointerdown.${tb.id}_pagingOnePageNum`);
        }
    });
}
/*
##################################################
   一覧の取得（サーバーサイドページング）
##################################################
*/
// 表示するページ（tb.paging.pageNum）の分だけAPIから取得して表示する。
// retryFlag … 表示中のページが無くなっていた場合に、別のページへ移して取得しなおしたか（1度だけ）
async requestBody( retryFlag = false ) {
    const tb = this;

    const onePageNum = tb.paging.onePageNum,
          offset = ( tb.paging.pageNum - 1 ) * onePageNum;

    try {
        const data = await tb.request( tb.params.rest( onePageNum, offset ) );

        const list = ( fn.typeof( tb.params.list ) === 'function')
            ? tb.params.list( data )
            : data;
        const rows = ( fn.typeof( list ) === 'array')? list: [];

        const total = Number( fn.cv( tb.params.total( data ), 0 ) );

        // 削除などで表示中のページが無くなっていた場合は、存在する最後のページへ移して取得しなおす
        if ( !rows.length && tb.paging.pageNum > 1 && !retryFlag ) {
            tb.paging.pageNum = ( total > 0 )? Math.ceil( total / onePageNum ): 1;
            return tb.requestBody( true );
        }

        tb.data.body = rows;
        tb.paging.num = total;
        tb.paging.pageMaxNum = Math.max( Math.ceil( total / onePageNum ), 1 );

        tb.setBody();
    } catch ( error ) {
        tb.error( error );
    }
}
/*
##################################################
   Set tBody
##################################################
*/
setBody() {
    const tb = this;

    tb.$.container.removeClass('tableError');
    tb.$.errorMessage.empty();

    // 表示するものがない
    if ( !tb.data.body.length ) {
        tb.$.container.addClass('noData');
        tb.$.message.html(`<div class="noDataMessage">`
        + fn.html.icon('stop')
        + getMessage.FTE00054
        + `</div>`);
    } else {
        tb.$.container.removeClass('noData');
        tb.$.message.empty();
    }

    tb.$.tbody.html( tb.tbodyHtml() );
    // 行を作りなおすと選択は解除されるため、選択に応じたボタンの状態も戻す
    tb.updateSelectStatus();
    tb.updateFooterStatus();

    tb.$.wrap.scrollTop(0);
    tb.workEnd();

    tb.$.table.addClass('tableReady');
}
/*
##################################################
   再読込
##################################################
*/
reload() {
    const tb = this;

    tb.workStart('table', 0 );
    tb.requestBody();
}
/*
##################################################
   エラー表示
##################################################
*/
error( error ) {
    const tb = this;

    console.error( error );

    tb.data.body = [];
    tb.$.tbody.empty();
    tb.updateSelectStatus();
    tb.$.container.addClass('tableError');
    tb.$.errorMessage.html(``
    + `<div class="errorBorder"></div>`
    + `<div class="errorTableContainer">`
        + `<div class="errorTitle">`
            + `<span class="errorTitleInner">${fn.html.icon('circle_exclamation')}`
                + `${fn.cv( tb.option.errorTitle, getMessage.FTE14034, true )}</span>`
        + `</div>`
        + `<table class="table errorTable">`
            + `<tbody class="tbody">`
                + `<tr class="tBodyTr tr">`
                    + `<td class="tBodyTd td">`
                        + `<div class="ci textOverWrap">${fn.escape( fn.cv( error?.message, ''), true )}</div>`
                    + `</td>`
                + `</tr>`
            + `</tbody>`
        + `</table>`
    + `</div>`);

    tb.workEnd();
    tb.$.table.addClass('tableReady');
}
/*
##################################################
   プラットフォームAPIへのリクエスト
##################################################
*/
// 応答の data だけを返す。
async request( url ) {
    const options = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${DataTablePF.getToken()}`
        }
    };

    // AIアシスタントと同じ条件で再送する（AiAssistantChatが読み込まれていない画面では素のfetch）
    const response = ( typeof AiAssistantChat !== 'undefined')
        ? await AiAssistantChat.fetchWithRetry( url, options, { retryStatuses: DataTablePF.retryStatuses })
        : await fetch( url, options );

    const json = await response.json().catch( () => null );
    if ( !response.ok ) {
        // platform APIはエラー時も message を返すため、あればそれを利用する
        const error = new Error( json?.message ?? `DataTablePF request failed: ${response.status}`);
        error.status = response.status;
        throw error;
    }
    // 応答は { result, message, ts, data } の形なので data のみを返す
    return json?.data ?? {};
}
static getToken() {
    return ( fn.getCmmonAuthFlag() )? CommonAuth.getToken():
        ( window.parent !== window && window.parent.getToken )? window.parent.getToken(): null;
}

}
