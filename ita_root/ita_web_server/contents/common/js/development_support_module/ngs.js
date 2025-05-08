////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / ngs.js
//
//   -----------------------------------------------------------------------------------------------
//
//   NEC Generative AI Service (NGS)
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
            this.apiKey = apiParam.apiKey;
            this.account = apiParam.account;
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
            const model = 'cotomi-pro';
            const endPoint = `/_proxy/ngs/ngs2-papi/v1/openai/deployments/${model}/chat/completions`;
            const body = JSON.stringify({
                "messages": [
                    {"role":"system", "content": "あなたは日本語で回答するAIアシスタントです"},
                    {"role":"system", "content": "あなたは回答の冒頭に「NGSからの回答は」とつけます"},
                    {"role":"user","content": prompt}
                ],
                // "temperature": 0.7,
                // "n": 1,
                // "stream": false,
                // "stop": null,
                // "max_tokens": 800,
                // "presence_penalty": 0,
                // "frequency_penalty": 0,
                // "logit_bias": {},
                "user": this.account
            })
            const request = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'api-key': this.apiKey
                },
                body: body
            }

            const response = await fetch(endPoint, request);
            const result = await response.json();
            resolve(result.choices[0].message.content);
        } catch ( error ) {
            reject( error );
        }
    });
}

}