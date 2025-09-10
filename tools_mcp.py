import gradio as gr
from typing import Union, Optional
from opcua import Client, ua


# ---helper function: Connect to OPC UA Server
def connect_to_server(server_url: str):
    client = Client(server_url)
    client.connect()
    print("Connected to Server")
    return client

# --- Tool 1: Read
def read_variable(parameter: str, nodeid: str, server_url:str):
    """
    Read an OPC UA variable by its NodeId and print its current value.

    Args:
        parameter (str): A descriptive name for the variable (for logging purposes).
        nodeid (str): The OPC UA NodeId string identifying the variable (e.g., 'ns=4;i=11').
        server_url (str): The server url you need to connect to.
    Returns:
        any: The current value of the variable, or None if the read fails.
    """
    client = None
    try:
        client = connect_to_server(server_url)
        node = client.get_node(nodeid)
        node_value = node.get_value()
        print(f"Helper: Current value of {parameter} is {node_value}")
        client.disconnect()
    except Exception as e:
        print(f"❌ Failed to read {parameter}: {e}")
        node_value = None

    return node_value
    
# --- Tool 2: Write
def write_variable(parameter: str, nodeid: str, datatype: str, value: Union[float, int, str], server_url:str):
    """
    Write a fixed value to a specific OPC UA variable.

    Args:
        parameter (str): A descriptive name for the variable (for logging purposes).
        nodeid (str): The OPC UA NodeId string identifying the variable (e.g., 'ns=4;i=11').
        datatype (str): The name of the OPC UA VariantType (e.g., "Float", "Int16", "String").
        value (Any): The value to set for the specified variable.
        server_url (str): The server url you need to connect to.
    Returns:
        Any: The new value of the variable after the write, or None if the write fails.
    """
    client = None
    try:
        client = connect_to_server(server_url)
        node = client.get_node(nodeid)
                
        # Convert datatype string to actual VariantType enum
        variant_type = getattr(ua.VariantType, datatype)
  
        if datatype == "Int16":
            value = int(value)
        if datatype == "Float":
                value = float(value)
        dv = ua.DataValue()
        dv.Value = ua.Variant(value, variant_type)

        node.set_attribute(ua.AttributeIds.Value, dv)
        new_node_value = node.get_value()

        print(f"Helper: Value of {parameter} now set to {new_node_value}")
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Failed to read {parameter}: {e}")
        new_node_value = None

    return new_node_value

# --- Tool 3: Adjust
def adjust_variable(parameter: str, nodeid: str, datatype: str, delta: Union[float, int, str], server_url: str, unit: Optional[str] = None):
    """
    Adjust an OPC UA variable by a specified amount, either absolute or percentage.

    Args:
        parameter (str): A descriptive name for the variable (for logging purposes).
        nodeid (str): The OPC UA NodeId string identifying the variable (e.g., 'ns=4;i=11').
        datatype (str): The name of the OPC UA VariantType (e.g., "Float", "Int16", "String").
        delta (Any): The amount to change the variable by. Take as stated in datatype (Float = 10.0; Int16 = 10)
        unit (Optional[str]): The unit of adjustment. If "percent", the delta is applied as a percentage of
                              the current value; otherwise, it is applied as an absolute change.
        server_url (str): The server url you need to connect to.
    Returns:
        Any: The new value of the variable after the adjustment, or None if the operation fails.
    """
    client = None
    new_node_value = None
    try:
        client = connect_to_server(server_url)
        node = client.get_node(nodeid)
        current = node.get_value()
        
        if unit == "percent":
            change = current * (delta / 100)
            print(change)
            if datatype == "Int16":
                change = int(change)
                print(change)
        else:   
            change = delta
        new_val = current + change
        if datatype == "Int16":
                new_val = int(new_val)
        if datatype == "Float":
                new_val = float(new_val)

        variant_type = getattr(ua.VariantType, datatype)

        dv = ua.DataValue()
        dv.Value = ua.Variant(new_val, variant_type)
        
        node.set_attribute(ua.AttributeIds.Value, dv)
        new_node_value = node.get_value()

        symbol = "+" if delta >= 0 else "-"
        print(f"Helper: Adjusted {parameter} by {symbol}{abs(change)} → {new_node_value}")
        client.disconnect()

    except Exception as e:
        print(f"❌ Failed to adjust: {e}")
    return new_node_value

#--- Create MCP-Server with Gradio

demo_read = gr.Interface(
    fn=read_variable,
    inputs=[gr.Textbox(label="Parameter"),gr.Textbox(label="Nodeid"), gr.Textbox(label="Server_URL")],
    outputs="text",
    title="Read Variable",
    description="Reads a variable from the OPC UA server."
)

demo_write = gr.Interface(
    fn=write_variable,
    inputs=[
        gr.Textbox(label="Parameter"),
        gr.Textbox(label="NodeId"),
        gr.Textbox(label="Datatype"),
        gr.Textbox(label="Value"),
        gr.Textbox(label="Server_URL")
    ],
    outputs="text",
    title="Write Variable",
    description="Writes a value to a machine parameter."
)


demo_adjust = gr.Interface(
    fn=adjust_variable,
    inputs=[
        gr.Textbox(label="Parameter"),
        gr.Textbox(label="NodeId"),
        gr.Textbox(label="Datatype"),
        gr.Number(label="Delta"),
        gr.Textbox(label="Unit (optional)"),
        gr.Textbox(label="Server_URL")
    ],
    outputs="text",
    title="Adjust Variable",
    description="Adjusts a machine parameter by a delta value or percentage."
)

app = gr.TabbedInterface(
    [demo_read, demo_write, demo_adjust],
    tab_names=["Read", "Write", "Adjust"]
)

if __name__ == "__main__":
    app.launch(mcp_server=True, share=True)