////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / gemini.js
//
//   -----------------------------------------------------------------------------------------------
//
//   Gemini API
//
////////////////////////////////////////////////////////////////////////////////////////////////////

export class DevelopmentSupportModule {
/*
##################################################
    Constructor
##################################################
*/
constructor() {
}
/*
##################################################
    Setup
##################################################
*/
setup(apiParam) {
    return new Promise(async ( resolve, reject ) => {
        try {
            const module = await import('https://esm.run/@google/generative-ai');
            const genAI = new module.GoogleGenerativeAI( apiParam.apiKey );
            const systemInstruction = [
                "あなたは日本語で回答するAIアシスタントです。",
                "あなたは回答の冒頭に「Geminiからの回答は」とつけます。"
            ]
            // const systemInstruction = [
            //     'あなたは親切なインフラエンジニアです。',
            //     'Ansible Playbookの記述方法を教えるのがあなたの仕事です。',
            //     'Ansible Playbookを答えるときはtasksのセクションの配下だけをtasksを含めずに切り出して答えます。',
            //     'Ansible Playbookのtasksのセクションを切り出したものを"Exastro IT Automation用 Playbook"と呼称します。',
            //     'Ansible moduleのインストールが必要な時は、別途Ansible moduleのインストール方法も教えてください。',
            //     'また、pythonのライブラリーのインストールが必要な時は、別途pythonのライブラリーのインストール方法も教えてください。',
            //     'Ansible Playbook内で指定する値は、冒頭でset_factで大文字の変数名の変数に代入してから使用してください。'
            // ]
            this.model = genAI.getGenerativeModel({
                model: 'gemini-1.5-flash',
                systemInstruction: systemInstruction.join("\n")
            });
            resolve();
        } catch ( error ) {
            reject( error );
        }
    });
}
/*
##################################################
    Send prompt
##################################################
*/
send( prompt ) {
    return new Promise(async ( resolve, reject ) => {
        try {
            const result = await this.model.generateContent( prompt );
            resolve( result.response.text() );
        } catch ( error ) {
            reject( error );
        }
    });
}

}