# iot_central_simple_gateway

Illustrates how to Device Provisioning Service (DPS) register devices to a simple gateway device so they are related in IoT Central.  The sample is written using Python 3 and requires a minimum version of 3.7

&nbsp;
## Whats this sample all about?

This is a simple sample that shows how to write a very simple gateway that registers itself with IoT Central and then registers three leaf devices (devices connected to the gateway) to IoT Central and forms a relationship between the leaf device and the gateway.  The end result of this is that the leaf devices will show up in IoT Central UX like this:

![Gateway and leaf devices in IoT Central](/assets/gateway_device_view.png)

The leaf devices are related to the gateway so it is easy to identify what devices are connect to which gateway.

The sample does not send telemetry or properties it just does the DPS registration of the gateway and then the DPS registration of the leaf devices and associates them with the gateway identity.

&nbsp;
## How do I set this up?

We need to setup the gateway and leaf device templates in IoT Central.  Let's do the leaf device first.  Go to Device Templates and click the **+** and add select **IoT device**.  Click **Next: Customize** and give the template a name of **leaf device**.  Click **Next: Review** and on the next screen **Create**.

Select **Import a model** and select the model file leafDeviceModel.json in this repository.  The device model will be imported and you can click **Publish** to publish the model ready for use.

Next we need to add the gateway device.  Go to Device Templates and click the **+** and add select **IoT device**.  Click **Next: Customize** and give the template a name of **gateway**.  We also need to check the **This is a gateway device** checkbox:

![Gateway checkbox](/assets/gateway_checkbox.png)

Click **Next: Review** and on the next screen **Create**.  Select **Import a model** and select the model file gatewayModel.json in this repository.  The device model will be imported but before we publish we need to add a relationship.  The relationship will associate the leaf device models with the gateway.  Use the **Target** dropdown and find the device model we added earlier (**leaf device**) and select it, the Display name and Name will be given default values.  

![Gateway relationship](/assets/gateway_relationship.png)

Now **Save** the template and then click **Publish** to publish the model ready for use.

&nbsp;
## How do I run the code?

Before we run the code we need to add in our scope id and group symmetric key at lines 21 and 22 of gateway.py

```python
# device settings - FILL IN YOUR VALUES HERE
scope_id = "<Put your scope id here from IoT Central Administration -> Device connection>"
group_symmetric_key = "<Put your group SAS primary key here from IoT Central Administration -> Device Connection -> SAS-IoT-Devices>"
```

After saving the file From the command line run either :

```shell
python gateway.py
```

or (depending on your environment):

```shell
python3 gateway.py
```

After running the code return to your IoT Central application and click on the **Devices** and you should see **my_gateway** device.  If you click on it you should see the following displayed:

![Gateway and leaf devices in IoT Central](/assets/gateway_device_view.png)
