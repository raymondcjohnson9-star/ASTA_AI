package com.asta.ai

import android.app.AppOpsManager
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.provider.Settings
import android.os.Process
import java.util.concurrent.TimeUnit

/**
 * Reads Android's aggregate app-usage totals for the previous seven days.
 * It does not read notifications, messages, screen contents, or keystrokes.
 * The caller must obtain the user's explicit Usage Access approval in Settings.
 */
object AppUsageObserver {
    fun hasUsageAccess(context: Context): Boolean {
        val appOps = context.getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager
        val mode = appOps.checkOpNoThrow(
            AppOpsManager.OPSTR_GET_USAGE_STATS,
            Process.myUid(),
            context.packageName
        )
        return mode == AppOpsManager.MODE_ALLOWED
    }

    fun openUsageAccessSettings(context: Context) {
        context.startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    }

    fun weeklySummary(context: Context, maxApps: Int = 12): String {
        if (!hasUsageAccess(context)) return "Usage access is not enabled."
        val manager = context.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
        val end = System.currentTimeMillis()
        val start = end - TimeUnit.DAYS.toMillis(7)
        val totals = manager.queryAndAggregateUsageStats(start, end)
            .values
            .filter { it.totalTimeInForeground > 0L && it.packageName != context.packageName }
            .sortedByDescending { it.totalTimeInForeground }
            .take(maxApps)
        if (totals.isEmpty()) return "No app-usage totals are available yet."
        val totalMinutes = totals.sumOf { TimeUnit.MILLISECONDS.toMinutes(it.totalTimeInForeground) }
        val top = totals.first()
        val topMinutes = TimeUnit.MILLISECONDS.toMinutes(top.totalTimeInForeground)
        val share = if (totalMinutes > 0L) (topMinutes * 100L / totalMinutes) else 0L
        val rows = totals.joinToString(separator = "\\n") {
            val minutes = TimeUnit.MILLISECONDS.toMinutes(it.totalTimeInForeground)
            "${it.packageName}: ${minutes / 60}h ${minutes % 60}m"
        }
        return "LOCAL 7-DAY APP SUMMARY\\nTop recorded app: ${top.packageName} (${share}% of the listed foreground time)\\n\\n$rows\\n\\nThis is screen-time data only. It does not explain why an app was used or judge whether the usage is good or bad."
    }
}
