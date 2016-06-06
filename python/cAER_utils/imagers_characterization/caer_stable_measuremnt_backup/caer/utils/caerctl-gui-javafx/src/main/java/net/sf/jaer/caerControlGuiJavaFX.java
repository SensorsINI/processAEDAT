package net.sf.jaer;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.SocketChannel;

import org.apache.commons.validator.routines.InetAddressValidator;
import org.apache.commons.validator.routines.IntegerValidator;

import com.google.common.collect.ImmutableList;

import javafx.application.Application;
import javafx.beans.property.BooleanProperty;
import javafx.beans.property.DoubleProperty;
import javafx.beans.property.FloatProperty;
import javafx.beans.property.IntegerProperty;
import javafx.beans.property.LongProperty;
import javafx.beans.property.StringProperty;
import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.control.TabPane;
import javafx.scene.control.TextField;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import net.sf.jaer.jaerfx2.CAERCommunication;
import net.sf.jaer.jaerfx2.GUISupport;
import net.sf.jaer.jaerfx2.SSHS;
import net.sf.jaer.jaerfx2.SSHS.SSHSType;
import net.sf.jaer.jaerfx2.SSHSJavaFX;
import net.sf.jaer.jaerfx2.SSHSNode;
import net.sf.jaer.jaerfx2.SSHSNode.SSHSAttrListener.AttributeEvents;

public final class caerControlGuiJavaFX extends Application {
	private final VBox mainGUI = new VBox(20);
	private SocketChannel controlSocket = null;
	private final ByteBuffer netBuf = ByteBuffer.allocateDirect(1024).order(ByteOrder.LITTLE_ENDIAN);

	public static void main(final String[] args) {
		// Launch the JavaFX application: do initialization and call start()
		// when ready.
		Application.launch(args);
	}

	@Override
	public void start(final Stage primaryStage) {
		if (GUISupport.checkJavaVersion(primaryStage)) {
			final VBox gui = new VBox(20);
			gui.getChildren().add(connectToCaerControlServerGUI());
			gui.getChildren().add(mainGUI);

			GUISupport.startGUI(primaryStage, gui, "cAER Control Utility (JavaFX GUI)", (event) -> {
				try {
					cleanupConnection();
				}
				catch (final IOException e) {
					// Ignore this on closing.
				}
			});
		}
	}

	private HBox connectToCaerControlServerGUI() {
		final HBox connectToCaerControlServerGUI = new HBox(10);

		// IP address to connect to.
		final TextField ipAddress = GUISupport.addTextField(null, CAERCommunication.DEFAULT_IP);
		GUISupport.addLabelWithControlsHorizontal(connectToCaerControlServerGUI, "IP address:",
			"Enter the IP address of the cAER control server.", ipAddress);

		ipAddress.textProperty().addListener((valueRef, oldValue, newValue) -> {
			// Validate IP address.
			final InetAddressValidator ipValidator = InetAddressValidator.getInstance();

			if (ipValidator.isValidInet4Address(newValue)) {
				ipAddress.setStyle("");
			}
			else {
				ipAddress.setStyle("-fx-background-color: #FF5757");
			}
		});

		// Port to connect to.
		final TextField port = GUISupport.addTextField(null, CAERCommunication.DEFAULT_PORT);
		GUISupport.addLabelWithControlsHorizontal(connectToCaerControlServerGUI, "Port:",
			"Enter the port of the cAER control server.", port);

		port.textProperty().addListener((valueRef, oldValue, newValue) -> {
			// Validate port.
			final IntegerValidator portValidator = IntegerValidator.getInstance();

			if (portValidator.isInRange(Integer.parseInt(newValue), 1, 65535)) {
				port.setStyle("");
			}
			else {
				port.setStyle("-fx-background-color: #FF5757");
			}
		});

		// Connect button.
		GUISupport.addButtonWithMouseClickedHandler(connectToCaerControlServerGUI, "Connect", true, null, (event) -> {
			try {
				cleanupConnection();

				controlSocket = SocketChannel
					.open(new InetSocketAddress(ipAddress.getText(), Integer.parseInt(port.getText())));

				mainGUI.getChildren().add(caerControlGuiJavaFX.saveLoadInterface());
				mainGUI.getChildren().add(populateInterface("/"));
			}
			catch (NumberFormatException | IOException e) {
				GUISupport.showDialogException(e);
			}
		});

		return (connectToCaerControlServerGUI);
	}

	private static Pane saveLoadInterface() {
		final HBox contentPane = new HBox(20);

		// Save current configuration button.
		GUISupport.addButtonWithMouseClickedHandler(contentPane, "Save Configuration", true, null, (event) -> {
			final File save = GUISupport.showDialogSaveFile("XML Config File", ImmutableList.of("*.xml"));
			if (save != null) {
				try (FileOutputStream saveOS = new FileOutputStream(save)) {
					SSHS.GLOBAL.getNode("/").exportSubTreeToXML(saveOS, ImmutableList.of("shutdown"));
				}
				catch (final Exception e) {
					// Ignore, no file exceptions realistically possible at this
					// point, due to checks performed in the GUISupport dialog.
					e.printStackTrace();
				}
			}
		});

		// Load new configuration button.
		GUISupport.addButtonWithMouseClickedHandler(contentPane, "Load Configuration", true, null, (event) -> {
			final File load = GUISupport.showDialogLoadFile("XML Config File", ImmutableList.of("*.xml"));
			if (load != null) {
				try (FileInputStream loadOS = new FileInputStream(load)) {
					SSHS.GLOBAL.getNode("/").importSubTreeFromXML(loadOS, true);
				}
				catch (final Exception e) {
					// Ignore, no file exceptions realistically possible at this
					// point, due to checks performed in the GUISupport dialog.
					e.printStackTrace();
				}
			}
		});

		return (contentPane);
	}

	// Add tabs recursively with configuration values to explore.
	private Pane populateInterface(final String node) {
		final VBox contentPane = new VBox(20);

		// Add all keys at this level.
		// First query what they are.
		CAERCommunication.sendCommand(controlSocket, netBuf, CAERCommunication.caerControlConfigAction.GET_ATTRIBUTES,
			node, null, null, null);

		// Read and parse response.
		final CAERCommunication.caerControlResponse keyResponse = CAERCommunication.readResponse(controlSocket, netBuf);

		if ((keyResponse.getAction() != CAERCommunication.caerControlConfigAction.ERROR)
			&& (keyResponse.getType() == SSHSType.STRING)) {
			// For each key, query its value type and then its actual value, and
			// build up the proper configuration control knob.
			for (final String key : keyResponse.getMessage().split("\0")) {
				// Query type.
				CAERCommunication.sendCommand(controlSocket, netBuf,
					CAERCommunication.caerControlConfigAction.GET_TYPES, node, key, null, null);

				// Read and parse response.
				final CAERCommunication.caerControlResponse typeResponse = CAERCommunication.readResponse(controlSocket,
					netBuf);

				if ((typeResponse.getAction() != CAERCommunication.caerControlConfigAction.ERROR)
					&& (typeResponse.getType() == SSHSType.STRING)) {
					// For each key and type, we get the current value and then
					// build the configuration control knob.
					for (final String type : typeResponse.getMessage().split("\0")) {
						// Query current value.
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.GET, node, key, SSHSType.getTypeByName(type),
							null);

						// Read and parse response.
						final CAERCommunication.caerControlResponse valueResponse = CAERCommunication
							.readResponse(controlSocket, netBuf);

						if ((valueResponse.getAction() != CAERCommunication.caerControlConfigAction.ERROR)
							&& (valueResponse.getType() != SSHSType.UNKNOWN)) {
							// This is the current value. We have everything.
							contentPane.getChildren()
								.add(generateConfigGUI(node, key, type, valueResponse.getMessage()));
						}
					}
				}
			}
		}

		// Then query available sub-nodes.
		CAERCommunication.sendCommand(controlSocket, netBuf, CAERCommunication.caerControlConfigAction.GET_CHILDREN,
			node, null, null, null);

		// Read and parse response.
		final CAERCommunication.caerControlResponse childResponse = CAERCommunication.readResponse(controlSocket,
			netBuf);

		if ((childResponse.getAction() != CAERCommunication.caerControlConfigAction.ERROR)
			&& (childResponse.getType() == SSHSType.STRING)) {
			// Split up message containing child nodes by using the NUL
			// terminator as separator.
			final TabPane tabPane = new TabPane();
			contentPane.getChildren().add(tabPane);

			for (final String childNode : childResponse.getMessage().split("\0")) {
				GUISupport.addTab(tabPane, populateInterface(node + childNode + "/"), childNode);
			}
		}

		return (contentPane);
	}

	private Pane generateConfigGUI(final String node, final String key, final String type, final String value) {
		final HBox configBox = new HBox(20);

		final Label l = GUISupport.addLabel(configBox, String.format("%s (%s):", key, type), null);

		l.setPrefWidth(200);
		l.setAlignment(Pos.CENTER_RIGHT);

		final SSHSNode nnode = SSHS.GLOBAL.getNode(node);

		switch (SSHSType.getTypeByName(type)) {
			case BOOL: {
				// Create SSHS attribute and initialize it.
				nnode.putBool(key, value.equals("true"));

				// Create GUI element and initialize it, get its backing value
				// property.
				final BooleanProperty backendValue = GUISupport.addCheckBox(configBox, null, value.equals("true"))
					.selectedProperty();

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.booleanConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.BOOL)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			case BYTE: {
				// Create SSHS attribute and initialize it.
				nnode.putByte(key, Byte.parseByte(value));

				// Create GUI element and initialize it, get its backing value
				// property.
				final IntegerProperty backendValue = GUISupport.addTextNumberFieldWithSlider(configBox,
					Byte.parseByte(value), 0, Byte.MAX_VALUE);

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.byteConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.BYTE)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			case SHORT: {
				// Create SSHS attribute and initialize it.
				nnode.putShort(key, Short.parseShort(value));

				// Create GUI element and initialize it, get its backing value
				// property.
				final IntegerProperty backendValue = GUISupport.addTextNumberFieldWithSlider(configBox,
					Short.parseShort(value), 0, Short.MAX_VALUE);

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.shortConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.SHORT)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			case INT: {
				// Create SSHS attribute and initialize it.
				nnode.putInt(key, Integer.parseInt(value));

				// Create GUI element and initialize it, get its backing value
				// property.
				final IntegerProperty backendValue = GUISupport.addTextNumberFieldWithSlider(configBox,
					Integer.parseInt(value), 0, Integer.MAX_VALUE);

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.integerConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.INT)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			case LONG: {
				// Create SSHS attribute and initialize it.
				nnode.putLong(key, Long.parseLong(value));

				// Create GUI element and initialize it, get its backing value
				// property.
				final LongProperty backendValue = GUISupport.addTextNumberFieldWithSlider(configBox,
					Long.parseLong(value), 0, Long.MAX_VALUE);

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.longConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.LONG)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			case FLOAT: {
				// Create SSHS attribute and initialize it.
				nnode.putFloat(key, Float.parseFloat(value));

				// Create GUI element and initialize it, get its backing value
				// property.
				final FloatProperty backendValue = GUISupport.addTextNumberFieldWithSlider(configBox,
					Float.parseFloat(value), Float.MIN_VALUE, Float.MAX_VALUE);

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.floatConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.FLOAT)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			case DOUBLE: {
				// Create SSHS attribute and initialize it.
				nnode.putDouble(key, Double.parseDouble(value));

				// Create GUI element and initialize it, get its backing value
				// property.
				final DoubleProperty backendValue = GUISupport.addTextNumberFieldWithSlider(configBox,
					Double.parseDouble(value), Double.MIN_VALUE, Double.MAX_VALUE);

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.doubleConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.DOUBLE)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			case STRING: {
				// Create SSHS attribute and initialize it.
				nnode.putString(key, value);

				// Create GUI element and initialize it, get its backing value
				// property.
				final StringProperty backendValue = GUISupport.addTextField(configBox, value).textProperty();

				// Connect the GUI value property to the SSHS attribute.
				SSHSJavaFX.stringConnector(backendValue, nnode, key);

				// Add listener to SSHS attribute to send changes back to cAER
				// control server.
				nnode.addAttributeListener(null, (cnode, userData, event, changeKey, changeType, changeValue) -> {
					if ((event == AttributeEvents.ATTRIBUTE_MODIFIED) && (changeType == SSHSType.STRING)
						&& changeKey.equals(key)) {
						CAERCommunication.sendCommand(controlSocket, netBuf,
							CAERCommunication.caerControlConfigAction.PUT, node, key, null, changeValue);
						CAERCommunication.readResponse(controlSocket, netBuf);
					}
				});

				break;
			}

			default:
				// Unknown value type, just display the returned string.
				GUISupport.addLabel(configBox, value, null);
				break;
		}

		return (configBox);
	}

	private void cleanupConnection() throws IOException {
		mainGUI.getChildren().clear();

		if (controlSocket != null) {
			controlSocket.close();
			controlSocket = null;
		}
	}
}
