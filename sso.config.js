module.exports = {
    apps: [{
        name: 'SSO-SMANDAK',
        script: 'gunicorn sso.wsgi --threads=3 --bind 127.0.0.1:8001;',
        merge_logs: true,
        autorestart: true,
        log_file: "logs/combined.outerr.log",
        out_file: "logs/out.log",
        error_file: "logs/err.log",
        log_date_format: "YYYY-MM-DD HH:mm Z",
        append_env_to_name: true,
        watch: false,
    }],
};