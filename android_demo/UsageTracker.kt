package com.studentguardian.demo

// In a real Android app, use UsageStatsManager.
// Required permission: android.permission.PACKAGE_USAGE_STATS

class UsageTracker {
    fun getTodayUsage(): Map<String, Int> {
        return mapOf(
            "YouTube" to 80,
            "Instagram" to 35,
            "Study App" to 50
        )
    }
}
