<template>
    <div id="app">
        <nav class="navbar navbar-dark bg-dark" id="navbar">
            <span class="navbar-brand mb-0 h1">EC2 Minecraft Server Control Panel</span>
        </nav>
        <div v-if="authenticated === false"> <Login v-on:updateParent="updateAuth"/> </div>
        <div v-else-if="authenticated === true"> <ManageServer v-on:updateParent="updateAuth"/> </div>
    </div>
</template>


<script>
import Login from "./views/Login.vue"
import ManageServer from "./views/ManageServer.vue"
export default {
    name: 'App',
    components: {
        Login,
        ManageServer
    },
    data() { return { authenticated: false } },

    mounted: function () { if (localStorage.getItem("token")) { this.authenticated = true } },

    methods: {
        updateAuth: function() { 
            if (this.authenticated) { localStorage.removeItem("token") }
            this.authenticated = !this.authenticated 
        }
    }
}
</script>

<style>
    @import './assets/css/bootstrap.min.css';
    #navbar {
        padding: 10px;
    }
    
</style>