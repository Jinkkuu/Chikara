document.getElementById("logout-button").addEventListener("click", function() {
    // Function to delete cookies
    function deleteCookie(name) {
        document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    }
    
    // Delete the username and password cookies
    deleteCookie("username");
    deleteCookie("password");
    
    // Refresh the page
    location.reload();
});
