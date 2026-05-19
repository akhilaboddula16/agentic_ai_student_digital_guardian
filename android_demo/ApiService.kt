package com.studentguardian.demo

// In a real Android app, replace these println calls with Retrofit/Ktor requests.
// The backend now expects a bearer token from the student login flow and supports
// usage sync through POST /usage/sync.

class ApiService {
    fun sendUsage(accessToken: String, appName: String, durationMinutes: Int, limitMinutes: Int) {
        println("Sending device usage to backend /usage/sync")
        println("Authorization=Bearer $accessToken")
        println("app=$appName duration=$durationMinutes limit=$limitMinutes")
    }

    fun fetchDailyPolicy(accessToken: String) {
        println("Fetch any parent-defined rules before deciding whether the app should be blocked locally.")
        println("Authorization=Bearer $accessToken")
    }
}
