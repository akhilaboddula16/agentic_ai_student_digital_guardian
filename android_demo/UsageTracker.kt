package com.studentguardian.demo

// Real Android integration should use UsageStatsManager and the
// PACKAGE_USAGE_STATS permission. This file still stays lightweight
// because the repo is not a full Android Studio project yet.

class UsageTracker {
    fun getTodayUsage(): Map<String, Int> {
        return mapOf(
            "YouTube" to 80,
            "Instagram" to 35,
            "Study App" to 50
        )
    }
}
