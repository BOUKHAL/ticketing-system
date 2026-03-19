<template>
  <AppShell
    title="Admin Panel"
    subtitle="Manage users and roles."
  >
    <template #actions>
      <div class="user-chip">
        <i class="pi pi-shield"></i>
        <span>{{ user.email }} (admin)</span>
      </div>

      <PButton
        label="Back to Tickets"
        icon="pi pi-ticket"
        outlined
        @click="$router.push('/tickets')"
      />
    </template>

    <div class="page-grid">
      <PCard class="surface-card">
        <template #title>Create User</template>

        <template #content>
          <div class="form-grid" style="max-width: 720px;">
            <div>
              <label class="field-label">Email</label>
              <PInputText v-model="createForm.email" class="full-width" />
            </div>

            <div>
              <label class="field-label">Password</label>
              <PPassword
                v-model="createForm.password"
                :feedback="false"
                toggleMask
                fluid
              />
            </div>

            <div>
              <label class="field-label">Role</label>
              <PSelect
                v-model="createForm.role"
                :options="roles"
                optionLabel="label"
                optionValue="value"
                class="full-width"
              />
            </div>

            <PButton
              label="Create User"
              icon="pi pi-user-plus"
              @click="createUser"
            />
          </div>
        </template>
      </PCard>

      <PCard class="surface-card">
        <template #title>All Users</template>

        <template #content>
          <PDataTable :value="users" paginator :rows="8" responsiveLayout="scroll">
            <PColumn field="email" header="Email" />
            <PColumn header="Role">
              <template #body="{ data }">
                <PSelect
                  v-model="data.role"
                  :options="roles"
                  optionLabel="label"
                  optionValue="value"
                  class="full-width"
                  @change="updateUser(data)"
                />
              </template>
            </PColumn>
            <PColumn header="Active">
              <template #body="{ data }">
                <PTag
                  :value="data.is_active ? 'active' : 'inactive'"
                  :severity="data.is_active ? 'success' : 'secondary'"
                />
              </template>
            </PColumn>
            <PColumn header="Actions" style="width: 180px;">
              <template #body="{ data }">
                <PButton
                  label="Deactivate"
                  size="small"
                  severity="danger"
                  text
                  :disabled="!data.is_active"
                  @click="deactivateUser(data.id)"
                />
              </template>
            </PColumn>
          </PDataTable>
        </template>
      </PCard>
    </div>
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
      users: [],
      roles: [
        { label: "Customer", value: "customer" },
        { label: "Agent", value: "agent" },
        { label: "Admin", value: "admin" },
      ],
      createForm: {
        email: "",
        password: "",
        role: "customer",
      },
    };
  },
  methods: {
    async fetchUsers() {
      const response = await api.get("users/");
      this.users = response.data;
    },
    async createUser() {
      await api.post("users/", this.createForm);
      this.createForm = {
        email: "",
        password: "",
        role: "customer",
      };
      await this.fetchUsers();
    },
    async updateUser(userItem) {
      await api.patch(`users/${userItem.id}/`, {
        role: userItem.role,
        is_active: userItem.is_active,
      });
      await this.fetchUsers();
    },
    async deactivateUser(id) {
      await api.post(`users/${id}/deactivate/`);
      await this.fetchUsers();
    },
  },
  mounted() {
    this.user = JSON.parse(localStorage.getItem("user") || "{}");
    this.fetchUsers();
  },
};
</script>