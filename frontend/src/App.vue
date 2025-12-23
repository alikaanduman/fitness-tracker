<template>
  <div class="app">
    <header class="header">
      <h1>💪 Fitness Tracker</h1>
      <div class="user-selector">
        <select v-model="selectedUserId" @change="selectUser">
          <option value="">Select User</option>
          <option v-for="user in users" :key="user.id" :value="user.id">{{ user.username }}</option>
        </select>
        <button @click="showUserForm = true">+ New User</button>
      </div>
    </header>

    <div v-if="showUserForm" class="modal">
      <div class="modal-content">
        <h2>Create User Profile</h2>
        <form @submit.prevent="createUser">
          <input v-model="userForm.username" placeholder="Username" required />
          <input type="email" v-model="userForm.email" placeholder="Email" required />
          <input type="number" v-model.number="userForm.age" placeholder="Age" />
          <input type="number" v-model.number="userForm.height_cm" placeholder="Height (cm)" />
          <input type="number" step="0.1" v-model.number="userForm.weight_kg" placeholder="Weight (kg)" />
          <div class="modal-buttons">
            <button type="submit">Create</button>
            <button type="button" @click="showUserForm = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="selectedUser" class="main-content">
      <div class="stats">
        <div class="stat-card">
          <h3>Total Workouts</h3>
          <p>{{ stats.total_workouts || 0 }}</p>
        </div>
        <div class="stat-card">
          <h3>Calories Burned</h3>
          <p>{{ stats.total_calories_burned || 0 }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Minutes</h3>
          <p>{{ stats.total_minutes || 0 }}</p>
        </div>
      </div>

      <button @click="showWorkoutForm = true" class="add-workout-btn">+ Add Workout</button>

      <div v-if="showWorkoutForm" class="modal">
        <div class="modal-content">
          <h2>Add Workout</h2>
          <form @submit.prevent="createWorkout">
            <input v-model="workoutForm.workout_type" placeholder="Workout Type (e.g., Running, Gym)" required />
            <input type="number" v-model.number="workoutForm.duration_minutes" placeholder="Duration (minutes)" required />
            <input type="number" v-model.number="workoutForm.calories_burned" placeholder="Calories Burned" />
            <input type="date" v-model="workoutForm.date" required />
            <textarea v-model="workoutForm.notes" placeholder="Notes (optional)" rows="3"></textarea>
            <div class="modal-buttons">
              <button type="submit">Add</button>
              <button type="button" @click="showWorkoutForm = false">Cancel</button>
            </div>
          </form>
        </div>
      </div>

      <div class="workouts">
        <h2>Workout History</h2>
        <div v-for="workout in workouts" :key="workout.id" class="workout-card">
          <div class="workout-header">
            <h3>{{ workout.workout_type }}</h3>
            <span class="date">{{ new Date(workout.date).toLocaleDateString() }}</span>
          </div>
          <div class="workout-details">
            <span>⏱️ {{ workout.duration_minutes }} min</span>
            <span v-if="workout.calories_burned">🔥 {{ workout.calories_burned }} cal</span>
          </div>
          <p v-if="workout.notes" class="notes">{{ workout.notes }}</p>
        </div>
      </div>
    </div>

    <div v-else class="no-user">
      <p>Please select or create a user to start tracking workouts</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://localhost:5006/api'

export default {
  name: 'App',
  data() {
    return {
      users: [],
      selectedUserId: null,
      selectedUser: null,
      workouts: [],
      stats: {},
      showUserForm: false,
      showWorkoutForm: false,
      userForm: {
        username: '',
        email: '',
        age: null,
        height_cm: null,
        weight_kg: null
      },
      workoutForm: {
        workout_type: '',
        duration_minutes: null,
        calories_burned: null,
        date: new Date().toISOString().split('T')[0],
        notes: ''
      }
    }
  },
  mounted() {
    this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await axios.get(`${API_URL}/users`)
        this.users = response.data
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    },
    async selectUser() {
      if (this.selectedUserId) {
        try {
          const response = await axios.get(`${API_URL}/users/${this.selectedUserId}`)
          this.selectedUser = response.data
          this.fetchWorkouts()
          this.fetchStats()
        } catch (error) {
          console.error('Error fetching user:', error)
        }
      } else {
        this.selectedUser = null
      }
    },
    async fetchWorkouts() {
      try {
        const response = await axios.get(`${API_URL}/workouts?user_id=${this.selectedUserId}`)
        this.workouts = response.data
      } catch (error) {
        console.error('Error fetching workouts:', error)
      }
    },
    async fetchStats() {
      try {
        const response = await axios.get(`${API_URL}/workouts/stats?user_id=${this.selectedUserId}`)
        this.stats = response.data
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    },
    async createUser() {
      try {
        await axios.post(`${API_URL}/users`, this.userForm)
        this.userForm = { username: '', email: '', age: null, height_cm: null, weight_kg: null }
        this.showUserForm = false
        this.fetchUsers()
      } catch (error) {
        console.error('Error creating user:', error)
        alert('Error creating user')
      }
    },
    async createWorkout() {
      try {
        await axios.post(`${API_URL}/workouts`, {
          ...this.workoutForm,
          user_id: this.selectedUserId
        })
        this.workoutForm = {
          workout_type: '',
          duration_minutes: null,
          calories_burned: null,
          date: new Date().toISOString().split('T')[0],
          notes: ''
        }
        this.showWorkoutForm = false
        this.fetchWorkouts()
        this.fetchStats()
      } catch (error) {
        console.error('Error creating workout:', error)
      }
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-selector {
  display: flex;
  gap: 10px;
}

.user-selector select {
  padding: 10px;
  border-radius: 4px;
  border: none;
}

.user-selector button {
  padding: 10px 20px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  color: #7f8c8d;
  margin-bottom: 10px;
  font-size: 14px;
}

.stat-card p {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
}

.add-workout-btn {
  width: 100%;
  padding: 15px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 30px;
}

.workouts {
  background: white;
  padding: 25px;
  border-radius: 8px;
}

.workout-card {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.workout-card:last-child {
  border-bottom: none;
}

.workout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.workout-header h3 {
  color: #2c3e50;
}

.date {
  color: #7f8c8d;
  font-size: 14px;
}

.workout-details {
  display: flex;
  gap: 20px;
  color: #555;
  margin-bottom: 10px;
}

.notes {
  color: #7f8c8d;
  font-style: italic;
}

.no-user {
  text-align: center;
  padding: 100px;
  color: #95a5a6;
  font-size: 18px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal-content form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.modal-content input,
.modal-content textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-buttons {
  display: flex;
  gap: 10px;
}

.modal-buttons button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-buttons button[type="submit"] {
  background: #667eea;
  color: white;
}

.modal-buttons button[type="button"] {
  background: #ccc;
  color: #333;
}
</style>

