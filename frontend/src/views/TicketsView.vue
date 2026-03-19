<template>
  <AppShell
    title="Tickets"
    subtitle="Your ticket list is automatically filtered by your role."
  >
    <PToast />
    <template #actions>
      <div class="user-chip">
        <i class="pi pi-user"></i>
        <span>{{ user.email }} ({{ user.role }})</span>
      </div>

      <PButton
        v-if="user.role === 'customer'"
        label="Create Ticket"
        icon="pi pi-plus"
        @click="$router.push('/tickets/create')"
      />

      <PButton
        v-if="user.role === 'admin'"
        label="Admin Panel"
        icon="pi pi-cog"
        severity="secondary"
        @click="$router.push('/admin')"
      />

      <PButton
        label="Logout"
        icon="pi pi-sign-out"
        severity="contrast"
        outlined
        @click="logout"
      />
    </template>

    <PCard class="surface-card">
      <template #content>
        <PDataTable
          :value="tickets"
          paginator
          :rows="8"
          v-if="tickets.length"
          responsiveLayout="scroll"
        >
          <PColumn field="title" header="Title" />
          <PColumn header="Status">
            <template #body="{ data }">
              <PTag :value="data.status" :severity="statusSeverity(data.status)" />
            </template>
          </PColumn>
          <PColumn header="Priority">
            <template #body="{ data }">
              <PTag :value="data.priority" :severity="prioritySeverity(data.priority)" />
            </template>
          </PColumn>
          <PColumn field="created_by_email" header="Created By" />
          <PColumn header="Assigned To">
            <template #body="{ data }">
              {{ data.assigned_to_email || 'Not assigned' }}
            </template>
          </PColumn>
          <PColumn header="Actions" style="width: 140px;">
            <template #body="{ data }">
              <PButton
                label="Open"
                size="small"
                text
                icon="pi pi-arrow-right"
                @click="$router.push(`/tickets/${data.id}`)"
              />
            </template>
          </PColumn>
        </PDataTable>

        <div v-else class="empty-state">
          No tickets found.
        </div>
      </template>
    </PCard>
  </AppShell>
</template>

<script>
import api from "../services/api";
import AppShell from "../components/AppShell.vue";

export default {
  components: { AppShell },
  data() {
    return {
      user: {},
      tickets: [],
    };
  },
  methods: {
    async fetchTickets() {
      const response = await api.get("tickets/");
      this.tickets = response.data;
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
    async logout() {
      try {
        const refresh = localStorage.getItem("refresh");
        if (refresh) {
          await api.post("auth/logout/", { refresh });
        }
      } catch (error) {
      }

      localStorage.clear();
      this.$router.push("/login");
    },
  },
  async mounted() {
  this.user = JSON.parse(localStorage.getItem("user") || "{}");
  await this.fetchTickets(); // await it

  if (this.$route && this.$route.query && this.$route.query.toast) {
    this.$toast.add({
      severity: "success",
      summary: "Done",
      detail: this.$route.query.toast,
      life: 3000,
    });
  }
},
};
</script>