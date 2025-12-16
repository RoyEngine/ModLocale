package second_in_command.skills.smallcraft

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class QuickAsTheWind : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {
       /* tooltip.addPara("Frigates and destroyers have much faster recovery of their shipsystem", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 33%% reduced shipsystem cooldown",0f, Misc.getTextColor(), Misc.getHighlightColor(), "33%")
        tooltip.addPara("   - 33%% increased shipsystem charge regeneration",0f, Misc.getTextColor(), Misc.getHighlightColor(), "33%")*/

        tooltip.addPara("根据船体等级，-33%%/25%%/10%%/5%% 舰船系统冷却时间", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("根据船体等级，+33%%/25%%/10%%/5%% 舰船系统回充速率", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addPara("所有护卫舰和驱逐舰 +20%% 非导弹武器备弹量和备弹恢复速率", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {


        var bonus = when(hullSize) {
            ShipAPI.HullSize.FRIGATE -> 33f
            ShipAPI.HullSize.DESTROYER -> 25f
            ShipAPI.HullSize.CRUISER -> 10f
            ShipAPI.HullSize.CAPITAL_SHIP -> 5f
            else -> 0f
        }

        stats!!.systemRegenBonus.modifyPercent(id, bonus)
        stats.systemCooldownBonus.modifyMult(id, 1 - bonus / 100)

        if (hullSize != ShipAPI.HullSize.FRIGATE && hullSize != ShipAPI.HullSize.DESTROYER) return

        stats.ballisticAmmoBonus.modifyPercent(id, 20f)
        stats.energyAmmoBonus.modifyPercent(id, 20f)

        stats.ballisticAmmoRegenMult.modifyPercent(id, 25f)
        stats.energyAmmoRegenMult.modifyPercent(id, 25f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

}