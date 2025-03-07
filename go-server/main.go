package main

import (
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
)

func main() {
	// Use the service name from docker-compose for FastAPI
	target, err := url.Parse("http://fastapi:8000")
	if err != nil {
		log.Fatal(err)
	}
	proxy := httputil.NewSingleHostReverseProxy(target)

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// Proxy API and htmx dynamic endpoints to FastAPI
		if strings.HasPrefix(r.URL.Path, "/api/") ||
			strings.HasPrefix(r.URL.Path, "/bookmarks") ||
			strings.HasPrefix(r.URL.Path, "/folders") ||
			strings.HasPrefix(r.URL.Path, "/bookmark-form") {
			proxy.ServeHTTP(w, r)
		} else {
			// Serve static files from the "frontend" directory
			fs := http.FileServer(http.Dir("./frontend"))
			fs.ServeHTTP(w, r)
		}
	})

	log.Println("Starting Go server on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
