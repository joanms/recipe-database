// This initialises the side-nav for small screens
$(document).ready(function() {
    $('.collapsible').collapsible();
    $('select').material_select();
    $(".button-collapse").sideNav();
            
// This initialises the dropdown menus in the forms
    $('select').material_select();

// This ensures that the text ares in the form resize automatically when they have dynamically generated content
    $('.materialize-textarea').trigger('autoresize');
});