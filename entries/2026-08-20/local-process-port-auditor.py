import socket
import subprocess
import platform

def get_process_name(pid):
    try:
        if platform.system() == 'Windows':
            cmd = ['tasklist', '/fi', f'pid eq {pid}', '/nh']
            output = subprocess.check_output(cmd).decode().split()
            return output[0] if output else 'Unknown'
        else:
            cmd = ['ps', '-p', str(pid), '-o', 'comm=']
            return subprocess.check_output(cmd).decode().strip()
    except Exception:
        return 'Access Denied'

def check_ports(port_range):
    print(f'{"PORT":<10} | {"STATUS":<10} | {"PROCESS"}')
    print('-' * 40)
    
    for port in port_range:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                pid = 'N/A'
                try:
                    if platform.system() == 'Windows':
                        cmd = ['netstat', '-ano']
                        output = subprocess.check_output(cmd, shell=True).decode()
                        for line in output.splitlines():
                            if f':{port}' in line:
                                pid = line.split()[-1]
                                break
                    else:
                        pid = subprocess.check_output(['lsof', '-ti', f':{port}']).decode().strip()
                except Exception:
                    pid = 'Unknown'
                
                proc_name = get_process_name(pid) if pid != 'N/A' else 'N/A'
                print(f'{port:<10} | {"BUSY":<10} | {proc_name} (PID: {pid})')
            else:
                print(f'{port:<10} | {"FREE":<10} | -')

def main():
    # Checking common dev ports
    target_ports = range(8000, 8081)
    check_ports(target_ports)

if __name__ == '__main__':
    main()
