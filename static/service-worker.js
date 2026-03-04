self.addEventListener("install", event => {
    console.log("Service Worker installiert");
});

self.addEventListener("activate", evt => {
    console.log("service-worker activated")
})

self.addEventListener("fetch", event => {
    // aktuell nur durchreichen
});