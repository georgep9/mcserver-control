<template>
    <div id="manageServer">
        <button v-bind:class="'btn btn-' + btnStartV" v-on:click="manage('start')" id="startBtn"> {{ btnStartT }}</button>
        <button v-bind:class="'btn btn-' + btnStopV" v-on:click="manage('stop')" id="stopBtn"> {{ btnStopT }}</button>
        <p id="error">{{ error_msg }}</p>
        <h5 id="recentActivity">Recent activity:</h5>
        <p v-for="log in logs" :key="log.id" id="log">{{ log }}</p>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ManageServer',
    data() {
        return {
            btnStartT: "Start",
            btnStartV: "primary",
            btnStopT: "Stop",
            btnStopV: "primary",
            error_msg: "",
            logs: [],
            logsInterval: undefined,
            streaming: "",
            ec2_state: ""
        }
    },

    mounted: function () {
        this.getCurrentStatus();
    },

    methods: {

        getCurrentStatus : function () {
            const path = `${process.env.VUE_APP_API_ENDPOINT}/status`;
            axios.get(path, {headers: { 'Authorization': `token ${localStorage.getItem('token')}` }})
                .then((res) => {
                    if (res.data.status === "success") {
                        const server_status = JSON.parse(res.data.server_status)
                        if (server_status.last_trigger === "start"){
                            if (server_status.start_state === "running") {
                                this.btnStartT = "Starting server";
                                this.btnStartV = "warning";
                                this.btnStopT = "Stop";
                                this.btnStopV = "secondary";
                                this.streaming = "start"
                                this.streamLogs("start")
                            } else if (server_status.start_state === "done") {
                                this.btnStartT = "Server started";
                                this.btnStartV = "success";
                                this.btnStopV = "primary";
                                this.logs = server_status.start_logs
                            }
                        } else if (server_status.last_trigger === "stop"){
                            if (server_status.stop_state === "running") {
                                this.btnStopT = "Shutting down server";
                                this.btnStopV = "warning";
                                this.btnStartT = "Start";
                                this.btnStartV = "secondary";
                                this.streaming = "stop"
                                this.streamLogs("stop")
                            } else if (server_status.stop_state === "done") {
                                this.btnStopT = "Server stopped";
                                this.btnStopV = "danger";
                                this.btnStartV = "primary";
                                this.logs = server_status.stop_logs
                            }
                        }
                    }
                    else { this.$emit('updateParent'); }
                })
                .catch((e) => {
                    console.log(e);
                    this.error_msg = e;
                })
        },

        stopStream : function() {
            clearInterval(this.logsInterval);
            this.logsInterval = undefined;
            if (this.streaming === "start"){
                this.btnStartT = "Server started";
                this.btnStartV = "success";
                this.btnStopV = "primary";
            }
            else if (this.streaming === "stop"){
                this.btnStopT = "Server stopped";
                this.btnStopV = "danger";
                this.btnStartV = "primary";
            }
            this.streaming = "";
        },

        streamLogs: function(route) {
            const path = `${process.env.VUE_APP_API_ENDPOINT}/${route}_logs`;
            this.logsInterval = setInterval((p=path) => {
                axios.get(p, {headers: { 'Authorization': `token ${localStorage.getItem('token')}` }})
                    .then((res) => {
                        if (res.data.status === "success"){
                            this.logs = JSON.parse(res.data.logs);
                            if (res.data.done) { this.stopStream(); }
                        } else {
                            this.stopStream();
                            this.$emit('updateParent');
                        }
                    })
                    .catch((error) => {
                        this.logs = error;
                        console.log(error);
                    });
            }, 250)
        },

        manage: function(route) {
            if (this.logsInterval == null){
                const path = `${process.env.VUE_APP_API_ENDPOINT}/${route}`;
                axios.get(path, {headers: { 'Authorization': `token ${localStorage.getItem('token')}` }})
                    .then((res) => {
                        console.log(res.data);
                        if (res.data.status === "success"){
                            if (route === "start"){
                                this.btnStartT = res.data.msg;
                                this.btnStartV = "warning";
                                this.btnStopT = "Stop";
                                this.btnStopV = "secondary";
                            } else if (route === "stop"){
                                this.btnStopT = res.data.msg;
                                this.btnStopV = "warning";
                                this.btnStartT = "Start";
                                this.btnStartV = "secondary";
                            }
                            this.streaming = route;
                            this.streamLogs(route);
                        } else {
                            this.$emit('updateParent');
                        }
                    })
                    .catch((e) => {
                        this.error_msg = e;
                        console.log(e);
                    });
            }
        }
    }
}
</script>

<style scoped>

#manageServer {
    margin: 10px;
}

button {
    display: block;
    margin-bottom: 10px;
    width: 300px;
}

#recentActivity {
    font-weight: bold;
}

p#log {
   margin: 0px;
   padding: 0px;
}
</style>