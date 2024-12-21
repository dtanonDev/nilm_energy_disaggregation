# NILM Energy Disaggregation Integration for Home Assistant

## Installation

1. Ensure you have the following Python dependencies installed:
   - numpy
   - scikit-learn
   - pandas

2. Copy the `nilm_energy_disaggregation` folder to your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/nilm_energy_disaggregation/
   ```

3. Restart Home Assistant

## Configuration

1. In the Home Assistant UI, go to Configuration > Integrations
2. Click '+ Add Integration'
3. Search for "NILM Energy Disaggregation"
4. Select the source energy consumption sensor

## Requirements

- Home Assistant 2023.x or later
- Python 3.9+
- Existing energy consumption sensor

## Troubleshooting

- Ensure the source sensor is providing power consumption in watts
- Check Home Assistant logs for any error messages
- Verify Python dependencies are installed

## Contributing

Contributions are welcome! Please submit issues and pull requests on GitHub.

## License

[Specify your license here]
