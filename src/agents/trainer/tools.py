import paramiko
import os
import json
from typing import Callable, Optional



def deploy_and_train(
        local_filepath : str,
        colab_host : str,
        colab_port : int,
        colab_password : str,
        on_telemetery : Optional[Callable[[dict], None ]] = None
):
    """
    Connects to Colab via SSH, uploads the training script, executes it, 
    and parses stdout line-by-line for live telemetry callbacks.
    """

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    filename = os.path.basename(local_filepath)
    remote_path = f"/content/{filename}"

    final_report = None
    error_logs = ""

    try:
        print(f"[Trainer Tool] Connecting to Colab at {colab_host}:{colab_port}...")
        ssh.connect(hostname=colab_host, port=colab_port, username="root", password=colab_password)
        
        # 1. SCP the file to Colab
        print(f"[Trainer Tool] Uploading {filename} to Colab...")
        sftp = ssh.open_sftp()
        sftp.put(local_filepath, remote_path)
        sftp.close()
        
        # 2. Execute the file remotely
        print(f"🚀 [Trainer Tool] Executing script on Colab GPU...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")

        for line in iter(stdout.readline, ""):
            line = line.strip()
            if not line:
                continue
            
            #Try to parse the line to json
            try:
                data = json.load(line)

                if data.get("delabs_telemetery") and on_telemetery:
                    on_telemetery(data)

                elif data.get("delabs_final_report"):
                    final_report = data

            except json.JSONDecodeError:
                # If it's just a normal print statement (like pip install logs), ignore or log it
                pass

        # 4. Check for crashes
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error_logs = stderr.read().decode('utf-8')
            print(f"❌ [Trainer Tool] Execution crashed:\n{error_logs}")
            return {"status": "failed", "error": error_logs}
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    
    finally:
        ssh.close()

    return {
        "status" : "success",
        "final_report" : final_report
    }

