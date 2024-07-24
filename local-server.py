import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    ".js": "application/javascript",
})

print(f"Serving at http://localhost:{PORT}")
print("To view the map, open a web browser and go to:")
print(f"http://localhost:{PORT}/property_map.html")
print(f"http://localhost:{PORT}/estate_agents_map.html")
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
