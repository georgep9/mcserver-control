<template>
    <div id="login">
        <div class="form-group" id="login-form">
            <form v-on:submit.prevent="login">
                <input id="pin" type="password" v-model="pin" class="form-control"/>
                <button class="btn btn-primary" id="login-btn">Login</button>
                <p id="error"> {{ feedback }} </p>
            </form>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'Login',
    data() {
        return {
            pin: "",
            feedback: ""
        }
    },
    methods: {
        login() {
            axios.post(`${process.env.VUE_APP_API_ENDPOINT}/api/login`, {pin: this.pin, payload: Date.now()})
                .then((res) => {
                    if (res.data.status === "success"){
                        localStorage.setItem('token', res.data.token)
                        this.$emit('updateParent')
                    } else {
                        this.feedback = "Error: Incorrect password.";
                    }
                })
                .catch((e) => {
                    console.log(e)
                    this.feedback = "Error: Internal server error";
                })
        }
    }
}
</script>

<style scoped>
#login-form {
    position: absolute;
    top: 50%;
    left: 50%;
    margin-right: -50%;
    transform: translate(-50%, -50%);

    width: 50%;
    max-width: 300px;
}
#login-btn {
    width: 100%;
    margin-top: 10px;
}
#error {
    color: red;
}
</style>
