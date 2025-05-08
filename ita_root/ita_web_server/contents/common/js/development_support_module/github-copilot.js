////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / github-copilot.js
//
//   -----------------------------------------------------------------------------------------------
//
//   NEC Generative AI Service (Github Copilot)
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
            const endPoint = `${window.location.origin}/_proxy/api.githubcopilot.com/chat/completions`;
            const body = JSON.stringify({
                "messages": [
                    {"role":"system", "content": "あなたは日本語で回答するAIアシスタントです"},
                    {"role":"system", "content": "あなたは回答の冒頭に「copilotからの回答は」とつけます"},
                    {"role":"user", "content":  prompt},
                ],
            })
            const request = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": `Bearer ${this.apiKey}`
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
