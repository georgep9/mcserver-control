<template>
    <div id="manageServer">
        <button v-bind:class="'btn btn-' + btnStartV" v-on:click="manage('start')" id="startBtn"> {{ btnStartT }}</button>
        <button v-bind:class="'btn btn-' + btnStopV" v-on:click="manage('stop')" id="stopBtn"> {{ btnStopT }}</button>
        <h5>Status: {{ manage_msg }}</h5>
        <h5>Logs:</h5>
        <p v-for="log in logs" :key="log.id" id="log">{{ log }}</p>
        <p> {{ server_status }} </p>
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
            manage_msg: "",
            logs: [],
            logsInterval: undefined,
            streaming: "",
            server_status: "",
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
                    console.log(res.data);
                    this.server_status = JSON.stringify(res.data.server_status)
                })
                .catch((e) => {
                    console.log(e);
                    this.manage_msg;
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
                        this.logs = JSON.parse(res.data.logs);
                        if (res.data.done) { this.stopStream(); }
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
                            console.log("here");
                            this.$emit('updateParent');
                        }
                    })
                    .catch((error) => {
                        this.manage_msg = error;
                        console.log(error);
                    });
            }
        }
    }
}
</script>

<style scoped>
p#log {
   margin: 0px;
   padding: 0px;
}
</style>