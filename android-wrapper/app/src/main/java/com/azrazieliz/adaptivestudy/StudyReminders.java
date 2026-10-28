package com.azrazieliz.adaptivestudy;

import android.Manifest;
import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import java.util.Calendar;
import org.json.JSONArray;
import org.json.JSONObject;

/** Local, no-network study reminders. One daily digest; no per-chapter spam. */
public final class StudyReminders extends BroadcastReceiver {
    private static final String PREF="adaptive_study_review_schedule";
    private static final String KEY="payload";
    private static final String CHANNEL="adaptive_study_due";
    private static final int REQUEST=7121;
    private static final int NOTIFICATION=7122;

    public static void update(Context ctx,String payload) {
        try {
            if (payload==null || payload.length()>100000) return;
            JSONObject obj=new JSONObject(payload);
            if (obj.optInt("version")!=1 || !(obj.opt("entries") instanceof JSONArray)) return;
            ctx.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putString(KEY,payload).apply();
            scheduleNext(ctx);
        } catch(Exception ignored) { }
    }

    private static PendingIntent alarmIntent(Context ctx) {
        Intent intent=new Intent(ctx,StudyReminders.class);
        intent.setAction("com.azrazieliz.adaptivestudy.REVIEW_ALARM");
        return PendingIntent.getBroadcast(ctx,REQUEST,intent,
            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    }

    private static long nextMorning() {
        Calendar cal=Calendar.getInstance();
        cal.set(Calendar.HOUR_OF_DAY,9);
        cal.set(Calendar.MINUTE,0);
        cal.set(Calendar.SECOND,0);
        cal.set(Calendar.MILLISECOND,0);
        if (cal.getTimeInMillis()<=System.currentTimeMillis()+60000)
            cal.add(Calendar.DAY_OF_YEAR,1);
        return cal.getTimeInMillis();
    }

    public static void scheduleNext(Context ctx) {
        try {
            SharedPreferences p=ctx.getSharedPreferences(PREF,Context.MODE_PRIVATE);
            JSONObject data=new JSONObject(p.getString(KEY,"{}"));
            AlarmManager am=(AlarmManager)ctx.getSystemService(Context.ALARM_SERVICE);
            if (am==null)return;
            PendingIntent pi=alarmIntent(ctx);
            am.cancel(pi);
            if (!data.optBoolean("enabled",false))return;
            // A daily scheduled check evaluates due dates after app inactivity.
            // Deliberately inexact: no exact-alarm special permission required.
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,nextMorning(),pi);
        } catch(Exception ignored) { }
    }

    @Override public void onReceive(Context ctx,Intent intent) {
        String action=intent==null?"":intent.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(action) ||
            Intent.ACTION_MY_PACKAGE_REPLACED.equals(action)) {
            scheduleNext(ctx);
            return;
        }
        if (!"com.azrazieliz.adaptivestudy.REVIEW_ALARM".equals(action))return;
        try {
            JSONObject obj=new JSONObject(ctx.getSharedPreferences(PREF,Context.MODE_PRIVATE)
                .getString(KEY,"{}"));
            if(!obj.optBoolean("enabled",false))return;
            JSONArray entries=obj.optJSONArray("entries");
            int due=0,weak=0;
            String first="";
            if(entries!=null)for(int i=0;i<entries.length();i++){
                JSONObject entry=entries.optJSONObject(i);
                if(entry==null||entry.optLong("due",Long.MAX_VALUE)>System.currentTimeMillis())continue;
                due++;
                if(entry.optInt("mastery",100)<75)weak++;
                if(first.isEmpty())first=entry.optString("title","");
            }
            if(due>0)notifyDue(ctx,due,weak,first);
        } catch(Exception ignored) { }
        finally {scheduleNext(ctx);}
    }

    private static void notifyDue(Context ctx,int due,int weak,String first) {
        NotificationManager nm=(NotificationManager)ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if(nm==null)return;
        if(Build.VERSION.SDK_INT>=33 &&
          ctx.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)return;
        if(Build.VERSION.SDK_INT>=26) {
            NotificationChannel channel=new NotificationChannel(CHANNEL,
              "Révisions des chapitres",NotificationManager.IMPORTANCE_DEFAULT);
            channel.setDescription("Rappels de sessions de questions et flashcards à effectuer");
            nm.createNotificationChannel(channel);
        }
        Intent open=new Intent(ctx,MainActivity.class);
        open.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pi=PendingIntent.getActivity(ctx,7118,open,
            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        String title=due==1?"1 chapitre à réviser":due+" chapitres à réviser";
        String body=due==1?first:first+" et "+(due-1)+" autre(s)";
        if(weak>0)body+=" · "+weak+" maîtrise(s) basse(s)";
        Notification.Builder n=Build.VERSION.SDK_INT>=26?
          new Notification.Builder(ctx,CHANNEL):new Notification.Builder(ctx);
        n.setSmallIcon(android.R.drawable.ic_popup_reminder)
         .setContentTitle(title)
         .setContentText(body)
         .setStyle(new Notification.BigTextStyle().bigText(body))
         .setAutoCancel(true).setContentIntent(pi)
         .setCategory(Notification.CATEGORY_REMINDER);
        nm.notify(NOTIFICATION,n.build());
    }
}
