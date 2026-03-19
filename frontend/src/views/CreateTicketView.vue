<template>
  <AppShell
    title="Create Ticket"
    subtitle="Customers can open a new ticket and set a priority."
  >
    <template #actions>
      <PButton
        label="Back"
        icon="pi pi-arrow-left"
        outlined
        @click="$router.push('/tickets')"
      />
    </template>

    <PCard class="surface-card">
      <template #content>
        <div class="form-grid">
          <div>
            <label class="field-label">Title</label>
            <PInputText v-model="form.title" class="full-width" />
          </div>

          <div>
            <label class="field-label">Priority</label>
            <PSelect
              v-model="form.priority"
              :options="priorities"
              optionLabel="label"
              optionValue="value"
              class="full-width"
            />
          </div>

          <div>
            <label class="field-label">Description</label>
            <MdEditor
              v-model="form.description"
              language="en-US"
              :preview="false"
              style="height: 300px;"
            />
          </div>

          <PButton
            label="Submit Ticket"
            icon="pi pi-check"
            @click="createTicket"
          />

          <PMessage v-if="error" severity="error">
            {{ error }}
          </PMessage>
        </div>
      </template>
    </PCard>
  </AppShell>
</template>

<script>
import api from "../services/api";
import AppShell from "../components/AppShell.vue";
import { MdEditor } from "md-editor-v3";
import "md-editor-v3/lib/style.css";

export default {
  components: { AppShell, MdEditor },
  data() {
    return {
      error: "",
      form: {
        title: "",
        description: "",
        priority: "medium",
      },
      priorities: [
        { label: "Low", value: "low" },
        { label: "Medium", value: "medium" },
        { label: "High", value: "high" },
      ],
    };
  },
  methods: {
    async createTicket() {
      this.error = "";

      try {
        await api.post("tickets/", this.form);
        this.$router.push("/tickets");
      } catch (error) {
        this.error = "Unable to create ticket.";
      }
    },
  },
};
</script>