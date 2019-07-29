// The code in this file is from the Materialize documentation

$(document).ready(function() {
// This initialises the side-nav for small screens
    $('.collapsible').collapsible();
    $('select').material_select();
    $(".button-collapse").sideNav();
            
// This initialises the dropdown menus in the forms
    $('select').material_select();

// This ensures that the text areas in the form resize automatically when they have dynamically generated content
    $('.materialize-textarea').trigger('autoresize');
});