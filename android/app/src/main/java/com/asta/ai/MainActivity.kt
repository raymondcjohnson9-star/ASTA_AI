package com.asta.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

private val Night = Color(0xFF07111B)
private val Panel = Color(0xFF101F2C)
private val Teal = Color(0xFF36E0C0)
private val Muted = Color(0xFF9BB0BF)
private val White = Color(0xFFEAF4F7)

data class ChatMessage(val text: String, val fromUser: Boolean)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { AstaApp() }
    }
}

@Composable
private fun AstaApp() {
    var endpoint by remember { mutableStateOf("") }
    var token by remember { mutableStateOf("") }
    var draft by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var showSettings by remember { mutableStateOf(true) }
    var status by remember { mutableStateOf("Connect your ASTA server to begin") }
    val messages = remember { mutableStateListOf(ChatMessage("Hello. I'm ASTA. Connect to your server and send me a message.", false)) }
    val scope = rememberCoroutineScope()
    val listState = rememberLazyListState()

    MaterialTheme(colorScheme = darkColorScheme(
        background = Night, surface = Panel, primary = Teal,
        onBackground = White, onSurface = White
    )) {
        Column(
            Modifier.fillMaxSize().background(Night).padding(16.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("ASTA", color = Teal, fontSize = 28.sp, fontWeight = FontWeight.Bold)
                    Text("PERSONAL AI ASSISTANT", color = Muted, fontSize = 10.sp, letterSpacing = 2.sp)
                }
                IconButton(onClick = { showSettings = !showSettings }) {
                    Icon(Icons.Default.Settings, contentDescription = "Connection settings", tint = Teal)
                }
            }
            Spacer(Modifier.height(12.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(8.dp).background(if (status.startsWith("Connected")) Teal else Muted, CircleShape))
                Spacer(Modifier.width(8.dp))
                Text(status, color = Muted, fontSize = 12.sp)
            }
            if (showSettings) {
                Spacer(Modifier.height(12.dp))
                Card(colors = CardDefaults.cardColors(containerColor = Panel), shape = RoundedCornerShape(16.dp)) {
                    Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("SERVER CONNECTION", color = Teal, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        OutlinedTextField(
                            value = endpoint, onValueChange = { endpoint = it },
                            modifier = Modifier.fillMaxWidth(),
                            label = { Text("HTTPS server address") },
                            placeholder = { Text("https://your-server.example") },
                            singleLine = true
                        )
                        OutlinedTextField(
                            value = token, onValueChange = { token = it },
                            modifier = Modifier.fillMaxWidth(),
                            label = { Text("Private access token") },
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)
                        )
                        Text("Keep your token private. Use a trusted HTTPS server.", color = Muted, fontSize = 11.sp)
                    }
                }
            }
            Spacer(Modifier.height(12.dp))
            LazyColumn(
                modifier = Modifier.weight(1f).fillMaxWidth(),
                state = listState,
                verticalArrangement = Arrangement.spacedBy(10.dp),
                contentPadding = PaddingValues(vertical = 8.dp)
            ) {
                items(messages) { item ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = if (item.fromUser) Arrangement.End else Arrangement.Start
                    ) {
                        Column(
                            Modifier.widthIn(max = 310.dp)
                                .background(if (item.fromUser) Color(0xFF123B3A) else Panel, RoundedCornerShape(16.dp))
                                .padding(13.dp)
                        ) {
                            Text(if (item.fromUser) "YOU" else "ASTA", color = if (item.fromUser) Teal else Muted, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                            Spacer(Modifier.height(4.dp))
                            Text(item.text, color = White, fontSize = 14.sp, lineHeight = 20.sp)
                        }
                    }
                }
                if (busy) item { Text("ASTA is thinking…", color = Teal, fontSize = 12.sp) }
            }
            Row(
                modifier = Modifier.fillMaxWidth().background(Panel, RoundedCornerShape(24.dp)).padding(7.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                BasicTextField(
                    value = draft,
                    onValueChange = { draft = it },
                    modifier = Modifier.weight(1f).padding(horizontal = 12.dp, vertical = 10.dp),
                    textStyle = TextStyle(color = White, fontSize = 14.sp),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                    keyboardActions = KeyboardActions(onSend = {
                        if (!busy && draft.isNotBlank()) {
                            val message = draft.trim()
                            draft = ""
                            messages.add(ChatMessage(message, true))
                            busy = true
                            scope.launch {
                                val answer = sendMessage(endpoint, token, message)
                                messages.add(ChatMessage(answer.first, false))
                                status = answer.second
                                busy = false
                                listState.animateScrollToItem(messages.lastIndex)
                            }
                        }
                    }),
                    decorationBox = { inner ->
                        if (draft.isEmpty()) Text("Message ASTA…", color = Muted)
                        inner()
                    }
                )
                IconButton(
                    enabled = !busy && draft.isNotBlank(),
                    onClick = {
                        val message = draft.trim()
                        draft = ""
                        messages.add(ChatMessage(message, true))
                        busy = true
                        scope.launch {
                            val answer = sendMessage(endpoint, token, message)
                            messages.add(ChatMessage(answer.first, false))
                            status = answer.second
                            busy = false
                            listState.animateScrollToItem(messages.lastIndex)
                        }
                    }
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Send message", tint = Teal)
                }
            }
        }
    }
}

private suspend fun sendMessage(base: String, token: String, message: String): Pair<String, String> =
    withContext(Dispatchers.IO) {
        if (base.isBlank() || token.isBlank()) return@withContext Pair(
            "Open settings and enter your server address and private access token.", "Not connected"
        )
        var connection: HttpURLConnection? = null
        try {
            val root = base.trim().removeSuffix("/")
            if (!root.startsWith("https://")) {
                return@withContext Pair("For safety, ASTA requires an HTTPS server address.", "HTTPS required")
            }
            connection = (URL("$root/api/chat").openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = 15000
                readTimeout = 60000
                doOutput = true
                setRequestProperty("Content-Type", "application/json; charset=utf-8")
                setRequestProperty("Authorization", "Bearer $token")
            }
            val body = JSONObject().put("message", message).toString().toByteArray(Charsets.UTF_8)
            connection.outputStream.use { it.write(body) }
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val raw = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
            val json = JSONObject(raw.ifBlank { "{}" })
            if (code in 200..299) {
                Pair(json.optString("answer", "ASTA returned an empty response."), "Connected to ASTA server")
            } else {
                Pair(json.optString("error", "Request failed ($code)."), "Server error: $code")
            }
        } catch (e: Exception) {
            Pair("I couldn't reach the ASTA server. Check the address, internet connection, and whether the server is running.", "Connection failed")
        } finally {
            connection?.disconnect()
        }
    }
