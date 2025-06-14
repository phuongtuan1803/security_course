from flask import Flask, request
import random
import json
 
app = Flask(__name__)
 
def fuzz_metric_value():
    return random.choice([
        random.uniform(-1e6, 1e6), 
    ])
   
def fuzz_json():
    return {
        "system.cpu": {
            "dimensions": {
                "user": {
                    "value": fuzz_metric_value()
                },
                "system": {
                    "value": fuzz_metric_value()
                }
            }
        },
        "system.uptime": {
            "dimensions": {
                "uptime": {
                    "value": fuzz_metric_value()
                }
            }
        },
        "sensors.temperature_cpu_thermal-virtual-0_temp1_input": {
            "dimensions": {
                "input": {
                    "value": fuzz_metric_value()
                }
            }
        },
        "system.ram": {
            "dimensions": {
                "free": {
                    "value": fuzz_metric_value()
                },
                "cached": {
                    "value": fuzz_metric_value()
                },
                "buffers": {
                    "value": fuzz_metric_value()
                },
                "used": {
                    "value": fuzz_metric_value()
                }
            }
        },
        "disk_space./": {
            "dimensions": {
                "used": {
                    "value": fuzz_metric_value()
                },
                "reserved_for_root": {
                    "value": fuzz_metric_value()
                },
                "avail": {
                    "value": fuzz_metric_value()
                }
            }
        }
    }
 
@app.route('/api/v1/allmetrics')
def allmetrics():
    fmt = request.args.get("format")
    print(f"[GET] allmetrics?format={fmt}")
    data = fuzz_json()
    # print(f"[FUZZ] Generated JSON:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
    return app.response_class(
        response=json.dumps(data, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)