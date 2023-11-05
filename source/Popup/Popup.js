var Popup = function () {
    return (
        React.createElement("section", { id: "popup" },
            React.createElement("h2", null, "Promptivity"),
            React.createElement("button", {
                id: "options__button",
                type: "button",
                onClick: function () {
                    return openWebPage('options.html');
                }
            }, "Options Page")
        )
    );
};
