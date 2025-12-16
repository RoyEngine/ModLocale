package second_in_command.skills.tactical

import com.fs.starfarer.api.GameState
import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.CampaignFleetAPI
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.misc.levelBetween
import second_in_command.specs.SCBaseSkillPlugin

class Spotters : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有护卫舰"
    }

    fun getFleetDP(fleet: CampaignFleetAPI) : Float {
        if (Global.getCurrentState() == GameState.TITLE) return 0f
        var DP = 0f
        for (member in fleet.fleetData.membersListCopy) {
            if (!member.isFrigate && !member.isDestroyer) continue
            DP += member.deploymentPointsCost
        }
        return DP
    }

    fun getBonus(fleet: CampaignFleetAPI) : Float {
        return 0.2f * getFleetDP(fleet).levelBetween(0f, 120f)
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("所有护卫舰 +1000 作战视距", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 这使他们能在更远的距离发现敌人",0f, Misc.getTextColor(), Misc.getHighlightColor(), "")

        tooltip.addSpacer(10f)

        var DP = getFleetDP(data.fleet).toInt()
        var bonus = (getBonus(data.fleet) * 100).toInt()

        tooltip.addPara("根据舰队中护卫舰的数量，增加舰队传感器范围", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 根据舰队中护卫舰的部署点数，减少幅度位于 0%%-20%% 之间",0f, Misc.getTextColor(), Misc.getHighlightColor(), "0%","20%")
        tooltip.addPara("   - 护卫舰达到 120 部署点数 时效果达到最大值",0f, Misc.getTextColor(), Misc.getHighlightColor(), "120 部署点数")
        tooltip.addPara("   - 舰队当前的部署点数为 $DP 点，提供 $bonus%% 的增益",0f, Misc.getTextColor(), Misc.getHighlightColor(), "$DP", "$bonus%")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        if (hullSize == ShipAPI.HullSize.FRIGATE) {
            stats!!.sightRadiusMod.modifyFlat(id, 1000f)
        }
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.sensorRangeMod.modifyMult("sc_spotters", 1f+getBonus(data.fleet), "观察测位")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.sensorRangeMod.unmodify("sc_spotters")
    }
}