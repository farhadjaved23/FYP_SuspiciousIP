document.addEventListener("DOMContentLoaded", function () {
    var containerDiv = document.getElementById("tableauViz");

    // Replace with your Tableau Public, Online, or Server dashboard link
    var url = "https://public.tableau.com/views/FYP_17392939514830/Sheet1?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link";

    var options = {
        hideTabs: true,  // Hides navigation tabs
        width: "100%",
        height: "800px",
        onFirstInteractive: function () {
            console.log("Tableau Dashboard Loaded Successfully!");
        }
    };

    var viz = new tableau.Viz(containerDiv, url, options);
});
