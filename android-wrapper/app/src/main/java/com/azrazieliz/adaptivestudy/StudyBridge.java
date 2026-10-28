package com.azrazieliz.adaptivestudy;

import android.Manifest;
import android.app.Activity;
import android.os.Build;
import android.content.Context;
import android.webkit.JavascriptInterface;

/** Minimal offline bridge. Only local JS can submit reminder schedules. */
public final class StudyBridge {
    private final Activity activity;
    StudyBridge(Activity activity) { this.activity=activity; }

    @JavascriptInterface
    public void requestNotifications() {
        activity.runOnUiThread(() -> {
            if (Build.VERSION.SDK_INT >= 33 &&
                    activity.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                            != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                activity.requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 6042);
            }
        });
    }

    @JavascriptInterface
    public void setReviewSchedule(String json) {
        // Bridge methods may execute off the UI thread; SharedPreferences/AlarmManager
        // can be accessed here without blocking WebView input.
        StudyReminders.update(activity.getApplicationContext(),json);
    }
}
