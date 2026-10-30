import os
import sys

def download_roboflow_dataset(api_key=None, workspace="v1-ui", project="ui-component-detection-2", version=1):
    """
    Downloads and prepares UI Component dataset from Roboflow Universe.
    """
    print(f"Preparing dataset '{workspace}/{project}' v{version}...")
    
    if api_key is None:
        api_key = os.environ.get("ROBOFLOW_API_KEY", "")

    if not api_key:
        print("Note: No ROBOFLOW_API_KEY provided.")
        print("To download directly from Roboflow Universe:")
        print("  1. Get a free API key at https://roboflow.com")
        print("  2. Run: python download_dataset.py --api_key YOUR_KEY")
        return False

    try:
        from roboflow import Roboflow
        rf = Roboflow(api_key=api_key)
        proj = rf.workspace(workspace).project(project)
        dataset = proj.version(version).download("yolov8")
        print(f"Dataset successfully downloaded to: {dataset.location}")
        return dataset.location
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return False

if __name__ == '__main__':
    key = sys.argv[1] if len(sys.argv) > 1 else None
    download_roboflow_dataset(api_key=key)
