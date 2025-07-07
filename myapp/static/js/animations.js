$(document).ready(function () {
    // Slide-in animation for auth-card
    $(".auth-card").hide().slideDown(500);

    // Fade-in animation for form groups
    $(".auth-form .form-group").each(function (index) {
        $(this).hide().delay(index * 100).fadeIn(500);
    });

    // Fade-in animation for buttons and links
    $(".auth-button").hide().delay(400).fadeIn(500);
    $(".auth-link").hide().delay(500).fadeIn(500);

    // Shake animation for validation errors
    $(".form-error").on("show", function () {
        $(this).css({ position: "relative" }).animate({ left: "-10px" }, 100)
            .animate({ left: "10px" }, 100)
            .animate({ left: "0px" }, 100);
    });
});
