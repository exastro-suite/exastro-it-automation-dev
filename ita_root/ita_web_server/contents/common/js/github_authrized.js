$(function() {
    const URI = {
        github_token: "/_proxy/github.com/login/oauth/access_token"
    }
    let progress = "";

    new Promise((resolve, reject) => {
        progress = "Github authlized code取得";

        console.log(progress);
        $("#progress").text(progress);

        // URLのquery stringからcodeパラメータを取得
        // codeパラメータはgithubから提供されるパラメータ
        auth_code = (new URLSearchParams(window.location.search).get("code"));
        if (auth_code == null || auth_code == "") {
            reject("Get github authlized code Faild");
            return;
        }
        resolve(auth_code);

    }).then((auth_code) => {
        return new Promise((resolve, reject) => {
            progress = "Github token発行中";

            console.log(progress);
            $("#progress").text(progress);

            //
            // githubのtoken endpointへ要求
            //
            const formData = new FormData();
            const llmClientId = window.opener.llmClientId;
            const llmClientSecret = window.opener.llmClientSecret;
            formData.append('client_id', llmClientId);
            formData.append('client_secret', llmClientSecret);
            formData.append('code', auth_code);

            $.ajax({
                "type": "POST",
                "url": URI.github_token,
                "data": formData,
                processData: false,
                contentType: false
            }).done((data, status, xhr) => {
                resolve(data);
            }).fail((jqXHR, textStatus, errorThrown) => {
                reject(`error status: ${textStatus}`);
            });
        });
    }).then((token_response) => {
        return new Promise((resolve, reject) => {
            progress = "Github token格納中";

            console.log(progress);
            $("#progress").text(progress);

            console.log(token_response);

            // githubのtoken endpointのレスポンスからaccess_tokenを取り出す
            let token = new URLSearchParams(token_response).get("access_token");

            if (token == null || token == "") {
                reject("Get github token Faild");
                return;
            }

            // cookieに格納する際の有効期限は、tokenの有効期限(デフォルト8時間)の1分前に設定
            let expires = new Date(new Date().getTime() + (parseInt(new URLSearchParams(token_response).get("expires_in")) - 60) * 1000); // 有効期限60秒前に失効

            // cookieに格納
            document.cookie = `github-app-token=${encodeURIComponent(token)};path=/; expires=${expires.toUTCString()};`;
            resolve();
        });
    }).then(() => {
        progress = "処理完了";

        console.log(progress);
        $("#progress").text(progress);

        $("#button_close").prop("disabled", false);

        const cookies = document.cookie.split(';');
        window.close();

    }).catch((reason) => {
        progress = "ERROR : " + reason;
        console.log(progress);
        $("#progress").text(progress);

        $("#button_close").prop("disabled", false);
    });
});