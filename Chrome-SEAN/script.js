$(document).ready(function() {
    $("#bt1").click(function() {
        // var url__ = "";
        chrome.tabs.query({ 'active': true, 'windowId': chrome.windows.WINDOW_ID_CURRENT },
            function(tabs) {
                url__ = tabs[0].url

                $.ajax({
                    url: "http://127.0.0.1:5000/",
                    // type: "post",
                    data: { 'data': url__ },
                    success: function(result) {
                        alert(result);
                    }
                });
            }
        );

    });
});