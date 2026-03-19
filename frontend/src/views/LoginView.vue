<template>
  <div class="page-wrap" style="max-width: 520px; padding-top: 200px;">
    <PCard class="surface-card">
      <template #title>Ticketing System</template>
      <template #subtitle>Sign in with your account</template>

      <template #content>
        <div class="form-grid">
          <div>
            <label class="field-label">Email</label>
            <PInputText v-model="email" type="email" class="full-width" />
          </div>

          <div>
            <label class="field-label">Password</label>
            <PPassword
              v-model="password"
              :feedback="false"
              toggleMask
              fluid
            />
          </div>

          <PButton label="Login" icon="pi pi-sign-in" @click="login" />

          <PMessage v-if="error" severity="error">
            {{ error }}
          </PMessage>
        </div>
      </template>
    </PCard>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      email: "",
      password: "",
      error: "",
    };
  },
  methods: {
    async login() {
      this.error = "";

      try {
        const response = await api.post("auth/login/", {
          email: this.email,
          password: this.password,
        });

        localStorage.setItem("access", response.data.access);
        localStorage.setItem("refresh", response.data.refresh);

        const payload = JSON.parse(atob(response.data.access.split(".")[1]));
        const user = {
          email: payload.email,
          role: payload.role,
        };

        localStorage.setItem("user", JSON.stringify(user));

        if (user.role === "admin") {
          this.$router.push("/admin");
        } else {
          this.$router.push("/tickets");
        }
      } catch (error) {
        this.error = "Invalid email or password.";
      }
    },
  },
};
</script>