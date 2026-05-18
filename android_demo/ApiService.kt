package com.studentguardian.demo

// In real Android app, use Retrofit or Ktor client to call FastAPI backend.

class ApiService {
    fun sendUsage(studentId: Int, appName: String, durationMinutes: Int, limitMinutes: Int) {
        println("Sending usage to backend")
        println("studentId=$studentId app=$appName duration=$durationMinutes limit=$limitMinutes")
    }
}
