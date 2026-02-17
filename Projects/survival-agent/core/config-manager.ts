/**
 * CONFIG MANAGER
 *
 * Implements @legendaryy's principle #2:
 * "config.patch > config.apply, always.
 * One partial apply can nuke your whole setup"
 *
 * Provides safe configuration management with:
 * - Partial updates (.patch)
 * - Version history
 * - Automatic rollback on errors
 * - Validation before apply
 */

import * as fs from 'fs';
import * as path from 'path';

interface ConfigVersion<T> {
  version: number;
  config: T;
  timestamp: number;
  description?: string;
}

export class ConfigManager<T extends Record<string, any>> {
  private config: T;
  private versions: ConfigVersion<T>[] = [];
  private configPath: string;
  private maxVersions: number;

  constructor(
    initialConfig: T,
    configPath: string,
    maxVersions: number = 10
  ) {
    this.config = { ...initialConfig };
    this.configPath = configPath;
    this.maxVersions = maxVersions;

    // Save initial version
    this.saveVersion('Initial configuration');

    // Load from disk if exists
    this.load();
  }

  /**
   * SAFE: Partially update configuration
   * Only updates specified fields, preserves others
   */
  patch(updates: Partial<T>, description?: string): T {
    const oldConfig = { ...this.config };

    try {
      // Merge updates into existing config
      this.config = {
        ...this.config,
        ...updates
      };

      // Validate new config
      this.validate(this.config);

      // Save version
      this.saveVersion(description || 'Partial update');

      // Persist to disk
      this.save();

      console.log(`✅ Config patched successfully`);
      if (description) {
        console.log(`   ${description}`);
      }

      return { ...this.config };

    } catch (error: any) {
      // Rollback on error
      console.error(`❌ Config patch failed: ${error.message}`);
      this.config = oldConfig;
      throw error;
    }
  }

  /**
   * UNSAFE: Full configuration replacement
   * Only use when you need to replace entire config
   */
  apply(newConfig: T, description?: string): T {
    const oldConfig = { ...this.config };

    try {
      // Replace entire config
      this.config = { ...newConfig };

      // Validate new config
      this.validate(this.config);

      // Save version
      this.saveVersion(description || 'Full replacement');

      // Persist to disk
      this.save();

      console.log(`⚠️  Config replaced entirely`);
      if (description) {
        console.log(`   ${description}`);
      }

      return { ...this.config };

    } catch (error: any) {
      // Rollback on error
      console.error(`❌ Config apply failed: ${error.message}`);
      this.config = oldConfig;
      throw error;
    }
  }

  /**
   * Get current configuration (read-only copy)
   */
  get(): Readonly<T> {
    return { ...this.config };
  }

  /**
   * Get specific config value
   */
  getValue<K extends keyof T>(key: K): T[K] {
    return this.config[key];
  }

  /**
   * Rollback to previous version
   */
  rollback(versionsBack: number = 1): T {
    if (this.versions.length <= 1) {
      throw new Error('No previous versions to rollback to');
    }

    const targetIndex = Math.max(0, this.versions.length - 1 - versionsBack);
    const targetVersion = this.versions[targetIndex];

    this.config = { ...targetVersion.config };
    this.save();

    console.log(`🔄 Rolled back to version ${targetVersion.version} (${new Date(targetVersion.timestamp).toISOString()})`);
    if (targetVersion.description) {
      console.log(`   ${targetVersion.description}`);
    }

    return { ...this.config };
  }

  /**
   * Get version history
   */
  getHistory(): ConfigVersion<T>[] {
    return [...this.versions];
  }

  /**
   * Validate configuration
   * Override this method for custom validation
   */
  protected validate(config: T): void {
    // Base validation: ensure all required fields exist
    // Subclasses should override for specific validation
  }

  /**
   * Save current config as new version
   */
  private saveVersion(description?: string): void {
    const version: ConfigVersion<T> = {
      version: this.versions.length,
      config: { ...this.config },
      timestamp: Date.now(),
      description
    };

    this.versions.push(version);

    // Limit version history
    if (this.versions.length > this.maxVersions) {
      this.versions = this.versions.slice(-this.maxVersions);
      // Renumber versions
      this.versions.forEach((v, i) => v.version = i);
    }
  }

  /**
   * Persist config to disk
   */
  private save(): void {
    try {
      const data = {
        current: this.config,
        versions: this.versions
      };

      fs.writeFileSync(
        this.configPath,
        JSON.stringify(data, null, 2),
        'utf-8'
      );
    } catch (error: any) {
      console.error(`⚠️  Failed to save config to disk: ${error.message}`);
    }
  }

  /**
   * Load config from disk
   */
  private load(): void {
    try {
      if (!fs.existsSync(this.configPath)) {
        // No saved config, use initial
        this.save();
        return;
      }

      const data = JSON.parse(fs.readFileSync(this.configPath, 'utf-8'));

      if (data.current) {
        this.config = data.current;
      }

      if (data.versions && Array.isArray(data.versions)) {
        this.versions = data.versions;
      }

      console.log(`✅ Loaded config from ${this.configPath}`);
    } catch (error: any) {
      console.error(`⚠️  Failed to load config from disk: ${error.message}`);
      // Continue with in-memory config
    }
  }

  /**
   * Export config for backup
   */
  export(): string {
    return JSON.stringify({
      current: this.config,
      versions: this.versions
    }, null, 2);
  }

  /**
   * Import config from backup
   */
  import(jsonData: string): void {
    try {
      const data = JSON.parse(jsonData);

      if (!data.current) {
        throw new Error('Invalid backup format: missing current config');
      }

      this.config = data.current;

      if (data.versions && Array.isArray(data.versions)) {
        this.versions = data.versions;
      }

      this.save();

      console.log(`✅ Imported config from backup`);
    } catch (error: any) {
      throw new Error(`Failed to import config: ${error.message}`);
    }
  }
}

/**
 * Trading bot config with validation
 */
export interface TradingBotConfig {
  // Position limits
  maxConcurrentPositions: number;
  maxPositionSize: number;
  minBalance: number;

  // Risk management
  takeProfit: number;
  stopLoss: number;
  trailingStopPercent: number;
  maxDrawdown: number;

  // Scoring thresholds
  minScore: number;
  minSmartMoneyConfidence: number;
  minShockedScore: number;

  // Auto refill
  autoRefillThreshold: number;
  autoRefillAmount: number;

  // Intervals
  scanIntervalMs: number;
  monitorIntervalMs: number;
  maxHoldTimeMs: number;

  // Features
  paperMode: boolean;
  useJito: boolean;
}

/**
 * Trading bot config manager with validation
 */
export class TradingBotConfigManager extends ConfigManager<TradingBotConfig> {
  protected validate(config: TradingBotConfig): void {
    // Validate position limits
    if (config.maxConcurrentPositions < 1 || config.maxConcurrentPositions > 20) {
      throw new Error('maxConcurrentPositions must be between 1 and 20');
    }

    if (config.maxPositionSize <= 0 || config.maxPositionSize > 1) {
      throw new Error('maxPositionSize must be between 0 and 1');
    }

    // Validate risk thresholds
    if (config.takeProfit <= 0) {
      throw new Error('takeProfit must be positive');
    }

    if (config.stopLoss >= 0) {
      throw new Error('stopLoss must be negative');
    }

    if (config.trailingStopPercent <= 0 || config.trailingStopPercent >= 1) {
      throw new Error('trailingStopPercent must be between 0 and 1');
    }

    // Validate scoring thresholds
    if (config.minScore < 0 || config.minScore > 100) {
      throw new Error('minScore must be between 0 and 100');
    }

    if (config.minSmartMoneyConfidence < 0 || config.minSmartMoneyConfidence > 100) {
      throw new Error('minSmartMoneyConfidence must be between 0 and 100');
    }

    // Validate intervals
    if (config.scanIntervalMs < 1000) {
      throw new Error('scanIntervalMs must be at least 1000ms');
    }

    if (config.monitorIntervalMs < 1000) {
      throw new Error('monitorIntervalMs must be at least 1000ms');
    }
  }
}
