package com.azrazieliz.adaptivestudy;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.content.res.AssetManager;

import java.io.*;
import java.net.*;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private WebView webView;
    private AssetServer server;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);

        webView.setWebViewClient(new WebViewClient() {
            private boolean local(Uri u) {
                if (u == null) return false;
                String h = u.getHost();
                return "127.0.0.1".equals(h) || "localhost".equalsIgnoreCase(h);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (local(u)) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) {}
                return true;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                Uri u = Uri.parse(url);
                if (local(u)) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) {}
                return true;
            }
        });

        try {
            server = new AssetServer(getAssets());
            server.start();
            webView.loadUrl("http://127.0.0.1:" + server.getPort() + "/index.html?build=3242");
        } catch (Exception e) {
            webView.loadData("<html><body><h2>Adaptive Study</h2><pre>" + escape(e.toString()) + "</pre></body></html>",
                    "text/html", "UTF-8");
        }
    }

    private static String escape(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        if (server != null) server.closeServer();
        if (webView != null) webView.destroy();
        super.onDestroy();
    }

    static final class AssetServer extends Thread {
        private final AssetManager assets;
        private final ServerSocket serverSocket;
        private final ExecutorService pool = Executors.newCachedThreadPool();

        AssetServer(AssetManager assets) throws IOException {
            super("AdaptiveStudyAssetServer");
            this.assets = assets;
            this.serverSocket = new ServerSocket(39117, 50, InetAddress.getByName("127.0.0.1"));
            setDaemon(true);
        }

        int getPort() { return serverSocket.getLocalPort(); }

        @Override
        public void run() {
            while (!serverSocket.isClosed()) {
                try {
                    final Socket socket = serverSocket.accept();
                    pool.execute(() -> handle(socket));
                } catch (IOException e) {
                    if (!serverSocket.isClosed()) e.printStackTrace();
                }
            }
        }

        void closeServer() {
            try { serverSocket.close(); } catch (IOException ignored) {}
            pool.shutdownNow();
        }

        private void handle(Socket socket) {
            try (Socket s = socket;
                 BufferedReader r = new BufferedReader(new InputStreamReader(s.getInputStream(), "UTF-8"));
                 OutputStream out = new BufferedOutputStream(s.getOutputStream())) {

                String first = r.readLine();
                if (first == null || first.isEmpty()) return;
                String[] parts = first.split(" ");
                if (parts.length < 2) return;
                String method = parts[0].toUpperCase(Locale.ROOT);
                String target = parts[1];

                String line;
                do { line = r.readLine(); } while (line != null && !line.isEmpty());

                if (!"GET".equals(method) && !"HEAD".equals(method)) {
                    sendStatus(out, 405, "Method Not Allowed");
                    return;
                }

                int q = target.indexOf('?');
                if (q >= 0) target = target.substring(0, q);
                try { target = URLDecoder.decode(target, "UTF-8"); } catch (Exception ignored) {}
                if (target.equals("/") || target.isEmpty()) target = "/index.html";
                while (target.startsWith("/")) target = target.substring(1);
                if (target.contains("..")) {
                    sendStatus(out, 403, "Forbidden");
                    return;
                }

                String assetPath = "www/" + target;
                InputStream in;
                try {
                    in = assets.open(assetPath, AssetManager.ACCESS_STREAMING);
                } catch (IOException missing) {
                    sendStatus(out, 404, "Not Found");
                    return;
                }

                String mime = mime(target);
                String headers =
                        "HTTP/1.1 200 OK\r\n" +
                        "Content-Type: " + mime + "\r\n" +
                        "Cache-Control: no-cache\r\n" +
                        "X-Content-Type-Options: nosniff\r\n" +
                        "Connection: close\r\n\r\n";
                out.write(headers.getBytes("UTF-8"));

                if (!"HEAD".equals(method)) {
                    try (InputStream body = in) {
                        byte[] buf = new byte[32768];
                        int n;
                        while ((n = body.read(buf)) >= 0) {
                            if (n > 0) out.write(buf, 0, n);
                        }
                    }
                } else {
                    in.close();
                }
                out.flush();
            } catch (Exception ignored) {}
        }

        private static void sendStatus(OutputStream out, int code, String text) throws IOException {
            String body = code + " " + text;
            String h = "HTTP/1.1 " + code + " " + text + "\r\n" +
                    "Content-Type: text/plain; charset=utf-8\r\n" +
                    "Content-Length: " + body.getBytes("UTF-8").length + "\r\n" +
                    "Connection: close\r\n\r\n" + body;
            out.write(h.getBytes("UTF-8"));
            out.flush();
        }

        private static String mime(String p) {
            String x = p.toLowerCase(Locale.ROOT);
            if (x.endsWith(".html") || x.endsWith(".htm")) return "text/html; charset=utf-8";
            if (x.endsWith(".js")) return "application/javascript; charset=utf-8";
            if (x.endsWith(".css")) return "text/css; charset=utf-8";
            if (x.endsWith(".json") || x.endsWith(".webmanifest")) return "application/json; charset=utf-8";
            if (x.endsWith(".svg")) return "image/svg+xml";
            if (x.endsWith(".png")) return "image/png";
            if (x.endsWith(".jpg") || x.endsWith(".jpeg")) return "image/jpeg";
            if (x.endsWith(".webp")) return "image/webp";
            if (x.endsWith(".pdf")) return "application/pdf";
            if (x.endsWith(".zip") || x.endsWith(".cbz")) return "application/zip";
            if (x.endsWith(".txt") || x.endsWith(".md")) return "text/plain; charset=utf-8";
            return "application/octet-stream";
        }
    }
}
