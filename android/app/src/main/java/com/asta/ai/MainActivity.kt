package com.asta.ai

import android.os.Bundle
import androidx.compose.ui.platform.LocalContext
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
import androidx.compose.ui.text.input.PasswordVisualTransformation
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
    var workspaceTitle by remember { mutableStateOf("Conversation") }
    val context = LocalContext.current
    var usageSummary by remember { mutableStateOf("App usage is not connected. ASTA only reads aggregate app time after you grant access.") }
    var usageAccess by remember { mutableStateOf(AppUsageObserver.hasUsageAccess(context)) }
    var personalBrief by remember { mutableStateOf("Personal intelligence is generated from ASTA's saved conversation archive and memory when you request it.") }
    var briefLoading by remember { mutableStateOf(false) }
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
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Panel),
                shape = RoundedCornerShape(14.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 11.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(Modifier.size(7.dp).background(Teal, CircleShape))
                    Spacer(Modifier.width(9.dp))
                    Column {
                        Text("ACTIVE WORKSPACE", color = Muted, fontSize = 9.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                        Text(workspaceTitle, color = Teal, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
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
                            visualTransformation = PasswordVisualTransformation(),
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)
                        )
                        Text("Keep your token private. Use a trusted HTTPS server.", color = Muted, fontSize = 11.sp)
                        Divider(color = Muted.copy(alpha = 0.25f))
                        Text("APP-USE LEARNING", color = Teal, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        Text(
                            "With your permission, ASTA can view aggregate time spent in apps over the last 7 days. It cannot read messages, passwords, or screen contents. These totals stay on this phone and are not sent to your ASTA server.",
                            color = Muted, fontSize = 11.sp
                        )
                        Text(
                            if (usageAccess) "Usage access: enabled" else "Usage access: not enabled",
                            color = if (usageAccess) Teal else Muted, fontSize = 11.sp
                        )
                        Button(
                            onClick = {
                                usageAccess = AppUsageObserver.hasUsageAccess(context)
                                if (!usageAccess) {
                                    AppUsageObserver.openUsageAccessSettings(context)
                                } else {
                                    usageSummary = AppUsageObserver.weeklySummary(context)
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(if (usageAccess) "Refresh 7-day app usage" else "Choose whether to allow app-usage access")
                        }
                        Text(usageSummary, color = White, fontSize = 11.sp)
                        Divider(color = Muted.copy(alpha = 0.25f))
                        Text("PERSONAL INTELLIGENCE", color = Teal, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        Text(
                            "On request, ASTA summarizes recurring topics and project mentions from its saved chat history and memory. Your app-usage totals remain on this phone and are not uploaded.",
                            color = Muted, fontSize = 11.sp
                        )
                        Button(
                            enabled = !briefLoading,
                            onClick = {
                                briefLoading = true
                                scope.launch {
                                    personalBrief = fetchPersonalBrief(endpoint, token)
                                    briefLoading = false
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(if (briefLoading) "Preparing summary…" else "Review my personal intelligence")
                        }
                        Text(personalBrief, color = White, fontSize = 11.sp)
                        Text(
                            "Privacy controls in chat: 'show memory', 'forget: exact text', 'forget all memories', 'show conversation history', and 'clear conversation history'.",
                            color = Muted, fontSize = 10.sp
                        )
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
                                workspaceTitle = answer.third
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
                            workspaceTitle = answer.third
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


private suspend fun fetchPersonalBrief(base: String, token: String): String =
    withContext(Dispatchers.IO) {
        if (base.isBlank() || token.isBlank()) return@withContext "Connect your HTTPS server and access token first."
        var connection: HttpURLConnection? = null
        try {
            val root = base.trim().removeSuffix("/")
            if (!root.startsWith("https://")) return@withContext "For safety, ASTA requires an HTTPS server address."
            connection = (URL("$root/api/intelligence").openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = 12000
                readTimeout = 20000
                setRequestProperty("Authorization", "Bearer $token")
            }
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val raw = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
            val json = JSONObject(raw.ifBlank { "{}" })
            if (code !in 200..299) return@withContext json.optString("error", "Could not load the summary ($code).")
            val brief = json.optJSONObject("personal_brief") ?: return@withContext "ASTA did not return a personal summary."
            val output = StringBuilder()
            output.append("Saved memories: ").append(brief.optInt("saved_memories_count")).append("\n")
            output.append("Recent user turns analyzed: ").append(brief.optInt("conversation_turns_analyzed")).append("\n\n")
            val themes = brief.optJSONArray("themes")
            if (themes != null && themes.length() > 0) {
                output.append("Recurring topics:\n")
                for (i in 0 until themes.length()) {
                    val item = themes.getJSONObject(i)
                    output.append("• ").append(item.optString("topic")).append(" (")
                        .append(item.optInt("mentions")).append(" keyword matches)\n")
                }
            } else output.append("No recurring topic pattern found yet.\n")
            val projects = brief.optJSONArray("active_projects")
            if (projects != null && projects.length() > 0) {
                output.append("\nProject notes:\n")
                for (i in 0 until projects.length()) output.append("• ").append(projects.optString(i)).append("\n")
            }
            val suggestions = brief.optJSONArray("suggestions")
            if (suggestions != null && suggestions.length() > 0) {
                output.append("\nIdeas:\n")
                for (i in 0 until suggestions.length()) output.append("• ").append(suggestions.optString(i)).append("\n")
            }
            output.append("\n").append(brief.optString("limitations"))
            output.toString()
        } catch (e: Exception) {
            "Could not load the personal summary. Check the HTTPS server connection."
        } finally {
            connection?.disconnect()
        }
    }

private suspend fun sendMessage(base: String, token: String, message: String): Triple<String, String, String> =
    withContext(Dispatchers.IO) {
        if (base.isBlank() || token.isBlank()) return@withContext Triple(
            "Open settings and enter your server address and private access token.", "Not connected", "Conversation"
        )
        var connection: HttpURLConnection? = null
        try {
            val root = base.trim().removeSuffix("/")
            if (!root.startsWith("https://")) {
                return@withContext Triple("For safety, ASTA requires an HTTPS server address.", "HTTPS required", "Conversation")
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
                Triple(json.optString("answer", "ASTA returned an empty response."), "Connected to ASTA server", json.optJSONObject("workspace")?.optString("title", "Conversation") ?: "Conversation")
            } else {
                Triple(json.optString("error", "Request failed ($code)."), "Server error: $code", "Conversation")
            }
        } catch (e: Exception) {
            Triple("I couldn't reach the ASTA server. Check the address, internet connection, and whether the server is running.", "Connection failed", "Conversation")
        } finally {
            connection?.disconnect()
        }
    }
