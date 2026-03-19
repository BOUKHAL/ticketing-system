<template>
  <AppShell
    title="Ticket Detail"
    subtitle="Available actions depend on your role."
  >
    <template #actions>
      <PButton
        label="Back"
        icon="pi pi-arrow-left"
        outlined
        @click="$router.push(user.role === 'admin' ? '/admin' : '/tickets')"
      />
    </template>

    <div class="page-grid two-col">
      <PCard class="surface-card">
        <template #title>{{ ticket.title || 'Loading...' }}</template>

        <template #content>
          <div class="stack" v-if="ticket.id">

            <!-- View mode -->
            <div v-if="!isEditing" class="stack">
              <MdPreview :modelValue="ticket.description" />
              <PButton
                v-if="canEditBasicFields"
                label="Edit"
                icon="pi pi-pencil"
                severity="secondary"
                outlined
                @click="isEditing = true"
              />
            </div>

            <!-- Edit mode -->
            <div v-else class="stack">
              <div>
                <label class="field-label">Title</label>
                <PInputText v-model="editForm.title" class="full-width" />
              </div>

              <div>
                <label class="field-label">Description</label>
                <MdEditor
                  v-model="editForm.description"
                  language="en-US"
                  :preview="false"
                  style="height: 300px;"
                />
              </div>

              <div style="display: flex; gap: 10px;">
                <PButton
                  label="Save"
                  icon="pi pi-save"
                  @click="updateBasicFields"
                />
                <PButton
                  label="Cancel"
                  icon="pi pi-times"
                  severity="secondary"
                  outlined
                  @click="isEditing = false"
                />
              </div>
            </div>

            <PDivider />

            <div class="stack">
              <h3 style="margin: 0;">Messages</h3>

              <div class="message-list" v-if="messages.length">
                <div class="message-item" v-for="message in messages" :key="message.id">
                  <div class="message-meta">
                    {{ message.author_email }} • {{ formatDate(message.created_at) }}
                  </div>
                  <div>{{ message.body }}</div>
                </div>
              </div>

              <div v-else class="empty-state">
                No messages yet.
              </div>

              <div>
                <label class="field-label">Reply</label>
                <PTextarea v-model="newMessage" rows="4" class="full-width" />
              </div>

              <PButton
                label="Send Message"
                icon="pi pi-send"
                @click="addMessage"
              />

              <PMessage v-if="error" severity="error">
                {{ error }}
              </PMessage>
            </div>
          </div>
        </template>
      </PCard>

      <PCard class="surface-card">
        <template #title>Controls</template>

        <template #content>
          <div class="ticket-meta" v-if="ticket.id">
            <div class="meta-row">
              <span>Status</span>
              <PTag :value="ticket.status" :severity="statusSeverity(ticket.status)" />
            </div>

            <div class="meta-row">
              <span>Priority</span>
              <PTag :value="ticket.priority" :severity="prioritySeverity(ticket.priority)" />
            </div>

            <div class="meta-row">
              <span>Created By</span>
              <span>{{ ticket.created_by_email }}</span>
            </div>

            <div class="meta-row">
              <span>Assigned To</span>
              <span>{{ ticket.assigned_to_email || 'Not assigned' }}</span>
            </div>

            <div v-if="canManageStatus" class="stack">
              <label class="field-label">Update Status</label>
              <PSelect
                v-model="newStatus"
                :options="statuses"
                optionLabel="label"
                optionValue="value"
                class="full-width"
              />
              <PButton
                label="Save Status"
                icon="pi pi-sync"
                @click="updateStatus"
              />
            </div>

            <div v-if="user.role === 'admin'" class="stack">
              <label class="field-label">Update Priority</label>
              <PSelect
                v-model="newPriority"
                :options="priorities"
                optionLabel="label"
                optionValue="value"
                class="full-width"
              />
              <PButton
                label="Save Priority"
                icon="pi pi-flag"
                severity="secondary"
                @click="updatePriority"
              />
            </div>

            <div v-if="user.role === 'admin'" class="stack">
              <label class="field-label">Assign / Reassign Agent</label>
              <PSelect
                v-model="selectedAgent"
                :options="agentOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Choose an agent"
                class="full-width"
              />
              <PButton
                label="Save Assignment"
                icon="pi pi-user-edit"
                severity="secondary"
                @click="assignTicket"
              />
            </div>

            <div v-if="canCloseTicket" class="stack">
              <PButton
                label="Close Ticket"
                icon="pi pi-check-circle"
                severity="success"
                outlined
                @click="closeTicket"
              />
            </div>

            <div v-if="user.role === 'admin'" class="stack">
              <PButton
                label="Delete Ticket"
                icon="pi pi-trash"
                severity="danger"
                @click="deleteTicket"
              />
            </div>
          </div>
        </template>
      </PCard>
    </div>
  </AppShell>
</template>

<script>
import api from "../services/api";
import AppShell from "../components/AppShell.vue";
import { MdPreview, MdEditor } from "md-editor-v3";
import "md-editor-v3/lib/preview.css";
import "md-editor-v3/lib/style.css";

export default {
  components: { AppShell, MdPreview, MdEditor },
  props: ["id"],
  data() {
    return {
      pollingInterval: null,
      isEditing: false,
      user: {},
      ticket: {},
      messages: [],
      error: "",
      newMessage: "",
      newStatus: "open",
      newPriority: "medium",
      selectedAgent: null,
      agents: [],
      statuses: [
        { label: "Open", value: "open" },
        { label: "In Progress", value: "in_progress" },
        { label: "Resolved", value: "resolved" },
        { label: "Closed", value: "closed" },
      ],
      priorities: [
        { label: "Low", value: "low" },
        { label: "Medium", value: "medium" },
        { label: "High", value: "high" },
      ],
      editForm: {
        title: "",
        description: "",
      },
    };
  },
  computed: {
    canEditBasicFields() {
      if (!this.ticket.id) return false;
      return (
        (this.user.role === "customer" && this.ticket.created_by_email === this.user.email) ||
        this.user.role === "admin"
      );
    },
    canManageStatus() {
      return this.user.role === "agent" || this.user.role === "admin";
    },
    canCloseTicket() {
      return this.user.role === "agent" || this.user.role === "admin";
    },
    agentOptions() {
      return this.agents.map((agent) => ({
        label: agent.email,
        value: agent.id,
      }));
    },
  },
  methods: {
    async fetchTicket() {
      const response = await api.get(`tickets/${this.id}/`);
      this.ticket = response.data;
      this.newStatus = this.ticket.status;
      this.newPriority = this.ticket.priority;
      this.selectedAgent = this.ticket.assigned_to || null;
      this.editForm.title = this.ticket.title;
      this.editForm.description = this.ticket.description;
    },
    async fetchMessages() {
      const response = await api.get(`tickets/${this.id}/messages/`);
      this.messages = response.data;
    },
    async fetchAgents() {
      if (this.user.role !== "admin") return;
      const response = await api.get("users/");
      this.agents = response.data.filter((u) => u.role === "agent" && u.is_active);
    },
    async addMessage() {
      if (!this.newMessage.trim()) return;
      this.error = "";
      try {
        await api.post(`tickets/${this.id}/messages/`, {
          body: this.newMessage,
        });
        this.newMessage = "";
        await this.fetchMessages();
      } catch (error) {
        this.error = "Unable to send message.";
      }
    },
    async updateBasicFields() {
      this.error = "";
      try {
        await api.patch(`tickets/${this.id}/`, {
          title: this.editForm.title,
          description: this.editForm.description,
        });
        this.isEditing = false;
        await this.fetchTicket();
      } catch (error) {
        this.error = "Unable to update ticket.";
      }
    },
    async updateStatus() {
      this.error = "";
      try {
        await api.patch(`tickets/${this.id}/status/`, {
          status: this.newStatus,
        });
        if (this.user.role === "agent" && this.newStatus !== "open") {
          this.$router.push({
            path: "/tickets",
            query: { toast: "Status updated successfully." },
          });
          return;
        }
        await this.fetchTicket();
      } catch (error) {
        this.error = "Unable to update status.";
      }
    },
    async updatePriority() {
      this.error = "";
      try {
        await api.patch(`tickets/${this.id}/priority/`, {
          priority: this.newPriority,
        });
        await this.fetchTicket();
      } catch (error) {
        this.error = "Unable to update priority.";
      }
    },
    async assignTicket() {
      this.error = "";
      try {
        await api.patch(`tickets/${this.id}/assign/`, {
          assigned_to: this.selectedAgent,
        });
        await this.fetchTicket();
      } catch (error) {
        this.error = "Unable to assign ticket.";
      }
    },
    async closeTicket() {
      this.error = "";
      try {
        await api.post(`tickets/${this.id}/close/`);
        if (this.user.role === "agent") {
          this.$router.push({
            path: "/tickets",
            query: { toast: "Ticket closed successfully." },
          });
          return;
        }
        await this.fetchTicket();
      } catch (error) {
        this.error = "Unable to close ticket.";
      }
    },
    async deleteTicket() {
      this.error = "";
      try {
        await api.delete(`tickets/${this.id}/`);
        this.$router.push("/tickets");
      } catch (error) {
        this.error = "Unable to delete ticket.";
      }
    },
    statusSeverity(status) {
      if (status === "open") return "warning";
      if (status === "in_progress") return "info";
      if (status === "resolved") return "success";
      if (status === "closed") return "secondary";
      return null;
    },
    prioritySeverity(priority) {
      if (priority === "high") return "danger";
      if (priority === "medium") return "warning";
      return "success";
    },
    formatDate(value) {
      return new Date(value).toLocaleString();
    },
  },
  async mounted() {
    this.user = JSON.parse(localStorage.getItem("user") || "{}");
    await this.fetchTicket();
    await this.fetchMessages();
    await this.fetchAgents();

    this.pollingInterval = setInterval(() => {
    this.fetchMessages();
  }, 5000);
  },
  unmounted() {
  clearInterval(this.pollingInterval);
},
};
</script>