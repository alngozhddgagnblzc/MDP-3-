package com.example.a0321mdp

import android.app.VoiceInteractor
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.telecom.Call
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import com.google.android.gms.common.api.Response
import java.io.IOException
import okhttp3.*

class MainActivity : AppCompatActivity() {


        private fun fetchDataFromServer() {
            val url = "http://10.137.222.66:5000"

            val client = OkHttpClient()

            val request = Request.Builder()
                .url(url)
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    // 네트워크 오류 처리
                    e.printStackTrace()
                }

                override fun onResponse(call: Call, response: Response) {
                    // 응답 처리
                    val responseData = response.body?.string()
                    // 응답 데이터 처리
                    // 여기서 응답을 다루거나 필요한 작업을 수행할 수 있습니다.
                    // 예를 들어, UI 업데이트 등
                }
                override fun onCreate(savedInstanceState: Bundle?) {
                    super.onCreate(savedInstanceState)
                    setContentView(R.layout.activity_main)
                    val recommendButton: Button = findViewById(R.id.recommend)
                    recommendButton.setOnClickListener {
                        fetchDataFromServer()
                    }
            })
        }

        val button1: Button = findViewById(R.id.view)
        button1.setOnClickListener {
            val intent = Intent(this, view::class.java)
            startActivity(intent)
            finish()
        }
    }
}


*(미완성 코드입니다)*










